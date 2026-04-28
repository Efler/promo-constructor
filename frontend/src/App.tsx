import { RootProviders } from './app/providers/RootProviders'
import { AppRouter } from './app/router'

function App() {
  return (
    <RootProviders>
      <AppRouter />
    </RootProviders>
  )
}

export default App
