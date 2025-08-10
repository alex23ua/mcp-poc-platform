# MCP React Client

Beautiful React.js client for the MCP (Model Context Protocol) Platform.

## 🚀 Features

- **Modern UI**: Clean, responsive design with gradient backgrounds and smooth animations
- **Real-time Status**: Shows MCP server connection status
- **Interactive Form**: Text area with Enter to send (Shift+Enter for new lines)
- **Error Handling**: User-friendly error messages with dismissible alerts
- **Response Display**: Formatted response with tools used indicators
- **Mobile Responsive**: Works perfectly on desktop, tablet, and mobile devices

## 🛠️ Installation

```bash
# Navigate to the React client directory
cd mcp_react_client

# Install dependencies
npm install

# Start the development server
npm start
```

The app will open at [http://localhost:3000](http://localhost:3000)

## 🔧 Configuration

The client is pre-configured to connect to your FastAPI MCP server running on `http://localhost:8001`.

If you need to change the API URL, modify the `API_BASE_URL` constant in `src/App.js`:

```javascript
const API_BASE_URL = 'http://your-server:port';
```

## 📁 Project Structure

```
mcp_react_client/
├── public/
│   ├── index.html          # HTML template
│   └── manifest.json       # PWA manifest
├── src/
│   ├── App.js             # Main React component
│   ├── App.css            # Component styles
│   ├── index.js           # React entry point
│   └── index.css          # Global styles
├── package.json           # Dependencies and scripts
└── README.md             # This file
```

## 🎯 Usage

1. **Start your MCP server** (FastAPI backend):
   ```bash
   python mcp_host.py
   ```

2. **Start the React client**:
   ```bash
   npm start
   ```

3. **Open your browser** to [http://localhost:3000](http://localhost:3000)

4. **Enter your prompt** in the text area and click "Send" or press Enter

## 🎨 UI Features

- **Status Indicator**: Green dot = Connected, Yellow = Initializing, Red = Disconnected
- **Keyboard Shortcuts**: Enter to send, Shift+Enter for new lines
- **Loading States**: Spinner and disabled states during processing
- **Error Messages**: Dismissible error alerts with clear messaging
- **Response Formatting**: Clean display of results with tool usage indicators
- **Responsive Design**: Adapts to all screen sizes

## 🔌 API Integration

The client integrates with your FastAPI MCP server endpoints:

- `GET /health` - Health check and status
- `POST /prompt` - Send customer prompts
- `GET /` - Server information

## 🎭 Customization

You can easily customize:

- **Colors**: Modify the gradient and color variables in CSS
- **Layout**: Adjust spacing and sizing in `App.css`
- **Functionality**: Add new features in `App.js`
- **Styling**: Change fonts, animations, and effects

## 🚦 Development

```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

## 📱 Mobile Support

The app is fully responsive and includes:
- Touch-friendly interface
- Mobile-optimized layouts
- Proper viewport handling
- Accessible design elements

Built with ❤️ for the MCP Platform
