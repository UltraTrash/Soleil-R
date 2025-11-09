import starfield from './starfield1.jpg';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={starfield} className="App-starfield" alt="starfield" />
        <h1>Welcome to Soliel!</h1>
        <h2>Soliel is the web application you need to monitor outer space's various weather phenomena</h2>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
        </a>
      </header>
    </div>
  );
}
export default App;
