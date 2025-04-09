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
    document.querySelector('#popupTitle').innerHTML = 'About Yapper';
    document.querySelector('#popupContent').innerHTML = `
      <p>Yapper is an improved version of Twitter, with a much more suitable name, because let's be honest, people don't usually post anything of importance, they just yapping! Enjoy this hellhole of peoples thoughts and feelings nobody but themselves care about.</p>
    `;
  }

  const createYap = () => {
    document.querySelector('.overlay').style.display = 'flex';
    document.querySelector('#popupTitle').innerHTML = 'Create Yap';
    document.querySelector('#popupContent').innerHTML = `
      <form class="createYapForm">
        <label for="yapContent">Yap:</label>
        <textarea id="yapContent" name="yapContent" maxlength="250" placeholder="Hey #Yapper ..."></textarea>
        <div class="char-counter"><span id="charCount">250</span> characters left</div>
        <button type="submit">Post</button>
      </form>
    `;
    
    // set up the character counter after the popup content is added to the DOM
    setTimeout(() => {
      const textarea = document.getElementById('yapContent');
      const charCountElement = document.getElementById('charCount');
      
      // the default value of the character counter
      charCountElement.textContent = 250;
      
      // update character count on input event
      textarea.addEventListener('input', () => {
        const remaining = 250 - textarea.value.length;
        charCountElement.textContent = remaining;
        
        // change color to red if less than 20 characters left
        if (remaining < 20) {
          charCountElement.style.color = 'red';
        } else {
          charCountElement.style.color = '';
        }
      });
    }, 0);
  }

  const editYap = (yapContent) => {
    document.querySelector('.overlay').style.display = 'flex';
    document.querySelector('#popupTitle').innerHTML = 'Edit Yap';
    document.querySelector('#popupContent').innerHTML = `
      <form class="createYapForm">
        <label for="yapContent">Edit Yap:</label>
        <textarea id="yapContent" name="yapContent" maxlength="250" placeholder="Hey #Yapper ...">${ yapContent }</textarea>
        <div class="char-counter"><span id="charCount">250</span> characters left</div>
        <button type="submit">Update Yap</button>
      </form>
    `;
    
    // set up the character counter after the popup content is added to the DOM
    setTimeout(() => {
      const textarea = document.getElementById('yapContent');
      const charCountElement = document.getElementById('charCount');
      
      // the default value of the character counter
      charCountElement.textContent = 250;

      const remaining = 250 - textarea.value.length;
        charCountElement.textContent = remaining;
        
        // change color to red if less than 20 characters left
        if (remaining < 20) {
          charCountElement.style.color = 'red';
        } else {
          charCountElement.style.color = '';
        }
      
      // update character count on input event
      textarea.addEventListener('input', () => {
        const remaining = 250 - textarea.value.length;
        charCountElement.textContent = remaining;
        
        // change color to red if less than 20 characters left
        if (remaining < 20) {
          charCountElement.style.color = 'red';
        } else {
          charCountElement.style.color = '';
        }
      });
    }, 0);
  }

  const closePopup = () => {
    document.querySelector('.overlay').style.display = 'none';
  }

  if(window.location.pathname === '/login') {
    return (
      <div className="App">
        <header>
          <h1>Yapper</h1>
        </header>
        <main>
          <h2 className="authTitle">Login to Yapper</h2>
          <form className="loginForm">
            <div>
              <label for="loginUsername">Username:</label>
              <input type="text" id="loginUsername" name="loginUsername" />
              <label for="loginPassword">Password:</label>
              <input type="password" id="loginPassword" name="loginPassword" />
              <button type="submit">Login</button>
            </div>
          </form>
          <p className="logregText">Don't have an account? <a href="/register">Register</a></p>
        </main>
      </div>
    );
  }
  if(window.location.pathname === '/register') {
    return (
      <div className="App">
        <header>
          <h1>Yapper</h1>
        </header>
        <main>
          <h2 className="authTitle">Register a Yapper account</h2>
          <form className="registerForm">
            <div>
              <label for="registerUsername">Username:</label>
              <input type="text" id="registerUsername" name="registerUsername" />
              <label for="registerPassword">Password:</label>
              <input type="password" id="registerPassword" name="registerPassword" />
              <label for="registerPasswordRepeat">Repeat password:</label>
              <input type="password" id="registerPasswordRepeat" name="registerPasswordRepeat" />
              <button type="submit">Register</button>
            </div>
          </form>
          <p className="logregText">Already have an account? <a href="/login">Login</a></p>
        </main>
      </div>
    );
  }


  return (
    <div className="App">
      <div className="overlay">
        <div className="overlayCloser" onClick={closePopup}></div>
        <div className="popup">
          <div className="popupHeader">
            <h2 id="popupTitle"></h2>
            <button className="closePopup" title="Close" onClick={closePopup}>X</button>
          </div>
          <div id="popupContent"></div>
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
        <button className="createYap" onClick={createYap}>Create Yap</button>
        <div>
          <input type="text" placeholder="Search Yapper..." />
          <button className="searchBtn" title="Search"><img src={searchIcon} alt="search icon" /></button>
        </div>
      </div>
      <nav>
        <a href="/" className="pageSelected">Home</a>
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
            <button className="editYap" onClick={() => editYap(yap.content)}>Edit</button>
            <button className="deleteYap">Delete</button>
          </div>
        ))}
      </main>
    </div>
  );
}

export default App;
