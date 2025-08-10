
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# import asyncio
import json
import yaml
# import re
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import requests
# import httpx
from openai import OpenAI
import os
from pathlib import Path
import uvicorn
from contextlib import asynccontextmanager

env_path = Path(__file__).parent / '.env'
print(f"Looking for .env file at: {env_path.absolute()}")
print(f".env file exists: {env_path.exists()}")

# Load environment variables from .env file with explicit path
load_dotenv(dotenv_path=env_path)

# Pydantic models for request/response
class CustomerPrompt(BaseModel):
    prompt: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class PromptResponse(BaseModel):
    success: bool
    result: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    tools_used: List[str] = []

class MCPHost:
    def __init__(self, mcp_server_url, openai_api_key: Optional[str] = None):
        self.mcp_server_url = mcp_server_url
        self.client = OpenAI(api_key=openai_api_key)
        self.available_tools = []
        self.session = None  # Will store the HTTP session
        self.session_id = None  # Will store the MCP session ID if provided by server
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize MCP connection with proper handshake sequence and session management"""
        headers = {
            'accept': 'application/json, text/event-stream',
            'content-type': 'application/json'
        }
        
        init_payload = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "python-client",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }
        try:
            response = requests.post(self.mcp_server_url, headers=headers, json=init_payload)
            session_id = response.headers.get('mcp-session-id')
            self.session_id = session_id
            print(f"Session ID: {session_id}")
            
            if not session_id:
                print("No session ID received")
                return
            
            headers['Mcp-Session-Id'] = session_id
            
            init_complete_payload = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            
            requests.post(self.mcp_server_url, headers=headers, json=init_complete_payload)
            print("Initialization complete")
            
            # List available MCP Servertools
            list_tools_payload = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 1
            }
            response = requests.post(self.mcp_server_url, headers=headers, json=list_tools_payload)
            
            lines = response.text.split('\n')
            data_line = next((line for line in lines if line.startswith('data: ')), None)
            
            if data_line:
                json_data = data_line[6:]
                result = json.loads(json_data)
                for tool in result['result']['tools']:
                    print(f"Tool: {tool['name']}")
                    # Description: {name['description']}"
            else:
                print("No data found in response")
                print("Raw response:", response.text)

                
            if response.status_code == 200:
                print(response.text)
                lines = response.text.split('\n')
                data_line = next((line for line in lines if line.startswith('data: ')), None)

                if data_line:
                    json_data = data_line[6:]
                    result = json.loads(json_data)
                    self.available_tools =result['result']['tools']
                    print(f"Available tools: {[tool['name'] for tool in self.available_tools]}")

                self.is_initialized = True
                
                        
        except Exception as e:
            print(f"Error initializing MCP connection: {e}")
            import traceback
            traceback.print_exc()
            await self.cleanup()

    def create_tool_functions_for_openai(self) -> List[Dict]:
        """Convert MCP tools to OpenAI function calling format"""
        openai_tools = []
        for tool in self.available_tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": {
                        "type": "object",
                        "properties": tool["inputSchema"]["properties"],
                        "required": tool["inputSchema"].get("required", [])
                    }
                }
            }
            openai_tools.append(openai_tool)
        return openai_tools

    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific MCP tool with given arguments using persistent session"""
        if not self.is_initialized:# or not self.session:
            return "MCP Host not initialized. Call initialize() first."
            
        try:
            tool_payload = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            # Include session ID if available
            if self.session_id:
                tool_payload["params"]["sessionId"] = self.session_id

            headers = {
              'accept': 'application/json, text/event-stream',
              'content-type': 'application/json'
            }
            headers['Mcp-Session-Id'] = self.session_id
            response = requests.post(
                self.mcp_server_url,
                json=tool_payload,
                headers=headers
            )
            
            if response.status_code == 200:
                lines = response.text.split('\n')
                data_line = next((line for line in lines if line.startswith('data: ')), None)
  
                print(f"Tool call response: {data_line}")
                # Handle the response format from FastMCP
                if data_line:
                    json_data = data_line[6:]
                    result = json.loads(json_data)
                    result = result['result']['structuredContent']['result']
                    print(f"Add result: {result}")
                else:
                    print("No data found in response")
   
                if isinstance(result, dict):
                    # If result has content array (typical MCP format)
                    content = result.get("content", [])
                    if content and len(content) > 0:
                        return content[0].get("text", str(result))
                    else:
                        # Direct result value
                        return str(result)
                else:
                    # Direct string/number result
                    return str(result)
            else:
                error_msg = f"Error calling tool: {response.status_code} - {response.text}"
                print(error_msg)
                return error_msg
        except Exception as e:
            error_msg = f"Error: {e}"
            print(error_msg)
            return error_msg

    async def cleanup(self):
        """Clean up the session"""
        if self.session:
            await self.session.aclose()
            self.session = None
            self.session_id = None
            self.is_initialized = False

    async def process_prompt(self, prompt: str, system_instructions: str, gpt_model: str) -> str:
        """Process a customer prompt and invoke appropriate MCP tools"""
        if not self.is_initialized:
            return "MCP Host not initialized. Call initialize() first."
            
        if not self.available_tools:
            return "No tools available."

        # Create OpenAI tools format
        openai_tools = self.create_tool_functions_for_openai()
        
        try:
            # Use OpenAI to understand the prompt and decide which tools to call
            response = self.client.chat.completions.create(
                model=gpt_model,
                messages=[
                    {
                        "role": "system", 
                        "content": system_instructions
                    },
                    {"role": "user", "content": prompt}
                ],
                tools=openai_tools,
                tool_choice="auto"
            )

            message = response.choices[0].message
            results = []
            tool_names =[]
            # If the model wants to call tools
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    print(f"Calling tool: {tool_name} with arguments: {arguments}")
                    
                    # Call the MCP tool
                    result = await self.call_mcp_tool(tool_name, arguments)
                    results.append(f"Tool '{tool_name}' result: {result}")
                    tool_names.append(tool_name)

                # Generate a final response incorporating the tool results
                final_response = self.client.chat.completions.create(
                    model="gpt-5",
                    messages=[
                        {
                            "role": "system", 
                            "content": system_instructions
                        },
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": f"I've executed the requested tools. Results: {'; '.join(results)}"}
                    ]
                )
                
                return tool_names, final_response.choices[0].message.content
            else:
                return message.content

        except Exception as e:
            return f"Error processing prompt: {e}"

# Global MCP host instance
mcp_host: Optional[MCPHost] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global mcp_host
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY environment variable not set!")
        raise RuntimeError("OPENAI_API_KEY not found in environment variables")
    
    print(f"✅ OpenAI API key loaded successfully (ends with: ...{api_key[-4:]})")

    with open('config.yaml', 'r') as file:
        config_data = yaml.safe_load(file)
    mcp_server_url = config_data["mcp_application"]["mcp_server_url"]
    if not mcp_server_url:
        print("❌ ERROR: mcp_server_url not set in config.yaml!")
        raise RuntimeError("mcp_server_url not found in config.yaml")
    
    # Initialize MCP host
    mcp_host = MCPHost(mcp_server_url=mcp_server_url,openai_api_key=api_key)
    
    try:
        await mcp_host.initialize()
        print("🚀 FastAPI MCP Server started successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize MCP host: {e}")
        raise
    
    yield
    
    # Shutdown
    if mcp_host:
        print("🛑 Shutting down MCP host...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="MCP Customer Prompt API",
    description="FastAPI server that processes customer prompts using MCP tools",
    version="1.0.0",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://localhost:3001",  # Backup port
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    """Root endpoint with server information"""
    return {
        "message": "MCP Customer Prompt API",
        "version": "1.0.0",
        "status": "running",
        "mcp_initialized": mcp_host.is_initialized if mcp_host else False,
        "available_tools": [tool["name"] for tool in mcp_host.available_tools] if mcp_host else []
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mcp_initialized": mcp_host.is_initialized if mcp_host else False,
        "tools_count": len(mcp_host.available_tools) if mcp_host else 0
    }

@app.post("/prompt", response_model=PromptResponse)
async def process_customer_prompt(request: CustomerPrompt):
    """
    Main endpoint to process customer prompts using MCP tools
    
    This endpoint captures the customer prompt from line 285 of your original code
    and processes it using the MCP host.
    """
    global mcp_host
    
    if not mcp_host or not mcp_host.is_initialized:
        raise HTTPException(
            status_code=503, 
            detail="MCP host not initialized. Server may be starting up."
        )
    
    try:
        print(f"📝 Processing prompt from user {request.user_id}: {request.prompt}")
        with open('config.yaml', 'r') as file:
            config_data = yaml.safe_load(file)
        system_instructions = config_data["mcp_application"]["system_instructions"]
        print(f"Using system instructions: {system_instructions}")
        # Process the prompt (equivalent to line 285 in your original code)

        gpt_model = config_data["mcp_application"].get("gpt_model", "gpt-5")
        print(f"Using GPT model: {gpt_model}")
        mcp_tools, result = await mcp_host.process_prompt(request.prompt, system_instructions, gpt_model=gpt_model)

        print(f"✅ Prompt processed successfully. Tools used:")
        
        return PromptResponse(
            success=True,
            result=result,
            user_id=request.user_id,
            session_id=request.session_id,
            tools_used=mcp_tools # Placeholder for actual tools used"
        )
        
    except Exception as e:
        print(f"❌ Error processing prompt: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing prompt: {str(e)}"
        )

@app.get("/tools")
async def list_available_tools():
    """List all available MCP tools"""
    if not mcp_host or not mcp_host.is_initialized:
        raise HTTPException(
            status_code=503,
            detail="MCP host not initialized"
        )
    
    return {
        "tools": mcp_host.available_tools,
        "count": len(mcp_host.available_tools)
    }

# Example test endpoints
@app.post("/test/simple")
async def test_simple_prompt():
    """Test endpoint with a simple prompt"""
    test_prompt = "please greet Alexander and show him the result of 12 plus 7"
    
    request = CustomerPrompt(
        prompt=test_prompt,
        user_id="test_user",
        session_id="test_session"
    )
    
    return await process_customer_prompt(request)

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "mcp_host:app",
        host="localhost",
        port=8001,
        reload=True,
        log_level="info"
    )