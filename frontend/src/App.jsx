import searchIcon from './searchIcon.png';
import './App.css';

function App() {
  return (
    <div className="App">
      <header>
       <h1>Yapper</h1>
       <div className="header-buttons">
        <button>?</button>
        <button>X</button>
       </div>
      </header>
      <div className="action-area">
        <button className="createYap">Create Yap</button>
        <div>
          <input type="text" placeholder="Search Yapper..." />
          <button><img src={searchIcon} alt="search icon" /></button>
        </div>
      </div>
      <nav>
        <a href="#" className="pageSelected">Home</a>
      </nav>
      <main>
        <div className="yap">
          <div className="yap-header">
            <h2>@admin</h2>
            <p>19.03.2025 12:58</p>
          </div>
          <p>just setting up my yappr</p>
        </div>
        <div className="yap">
          <div className="yap-header">
            <h2>@guy</h2>
            <p>19.03.2025 11:25</p>
          </div>
          <p>hey there, this is my first yap, i hope to use this service a lot you know, I love how simple it is and stuff, great!</p>
        </div>
      </main>
    </div>
  );
}

export default App;
