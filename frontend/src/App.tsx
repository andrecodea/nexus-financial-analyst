// Creates C1 Chat interface

// Imports AI & UI components
import { C1Chat, ThemeProvider } from '@thesysai/genui-sdk'
import "@crayonai/react-ui/styles/index.css"
import './App.css'

// Creates the C1 Chat interface and returns it
function App() {
  return (
    <div className='app-container'>
      <ThemeProvider mode='dark'>
        <C1Chat apiUrl='/api/chat' agentName='Nexus Financial Analyst' logoUrl='src/assets/favicon.svg'/>
      </ThemeProvider>
    </div>
  )
}

export default App