import searchIcon from './searchIcon.png';
import './App.css';

function App() {

  // dummy data
  const yapps = [
    {
      id: 1,
      username: 'admin',
      date: '2025-03-19T12:58:00',
      content: 'just setting up my yappr'
    },
    {
      id: 2,
      username: 'guy',
      date: '2025-03-19T11:25:00',
      content: 'hey there, this is my first yap, i hope to use this service a lot you know, I love how simple it is and stuff, great!'
    },
    {
      id: 3,
      username: 'another guy',
      date: '2025-03-26T14:31:00',
      content: 'Keep yapping, man! -Joe Biden'
    },
  ];

  // sorts yapps by date
  const sortedYapps = yapps.sort((a, b) => new Date(b.date) - new Date(a.date));

  // displays an alert with information about Yapper
  const aboutYapper = () => {
    document.querySelector('.overlay').style.display = 'flex';
  }

  const closePopup = () => {
    document.querySelector('.overlay').style.display = 'none';
  }

  return (
    <div className="App">
      <div className="overlay">
        <div className="popup">
          <div className="popupHeader">
            <h2>About Yapper</h2>
            <button className="closePopup" title="Close" onClick={closePopup}>X</button>
          </div>
          <p>Yapper is an improved version of Twitter, with a much more suitable name, because let's be honest, people don't usually post anything of importance, they just yapping! Enjoy this hellhole of peoples thoughts and feelings nobody but themselves care about.</p>
        </div>
      </div>
      <header>
       <h1>Yapper</h1>
       <div className="header-buttons">
        <button className="infoBtn" title="About Yapper" onClick={aboutYapper}>?</button>
        <button className="logoutBtn" title="Logout">X</button>
       </div>
      </header>
      <div className="action-area">
        <button className="createYap">Create Yap</button>
        <div>
          <input type="text" placeholder="Search Yapper..." />
          <button className="searchBtn" title="Search"><img src={searchIcon} alt="search icon" /></button>
        </div>
      </div>
      <nav>
        <a href="#" className="pageSelected">Home</a>
      </nav>
      <main>
        {/* displays each yap in the object array */}
        { sortedYapps.map(yap => (
          <div key={yap.id} className="yap">
            <div className="yap-header">
              <h2>@{yap.username}</h2>
              {/* changes time from ISO to local (in this case, norwegian) format */}
              <p>{new Date(yap.date).toLocaleString('en-GB', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false })}</p>
            </div>
            <p>{yap.content}</p>
          </div>
        ))}
      </main>
    </div>
  );
}

export default App;
