import searchIcon from "./searchIcon.png";
import "./App.css";
import React from "react";

function App() {
    const [searchQuery, setSearchQuery] = React.useState("");
    const [tweets, setTweets] = React.useState([]);

  const fetchTweets = async () => {
    try {
      const response = await fetch("https://yapper-4qux.onrender.com/tweets", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setTweets(data);
      }
    } catch (error) {
      console.error("Error fetching tweets: ", error);
    }
  };

  React.useEffect(() => {
    if (localStorage.getItem("token")) {
      fetchTweets();
    }
  }, []);

  React.useEffect(() => {
    const token = localStorage.getItem("token");
    if (
      !token &&
      window.location.pathname !== "/login" &&
      window.location.pathname !== "/register"
    ) {
      window.location.href = "/login";
    }
  }, []);

  // sorts yapps by date
  const sortedYapps = tweets.sort(
    (a, b) => new Date(b.created_at) - new Date(a.created_at)
  );

  // displays an alert with information about Yapper
  const aboutYapper = () => {
    document.querySelector(".overlay").style.display = "flex";
    document.querySelector("#popupTitle").innerHTML = "About Yapper";
    document.querySelector("#popupContent").innerHTML = `
      <p>Yapper is an improved version of Twitter, with a much more suitable name, because let's be honest, people don't usually post anything of importance, they just yapping! Enjoy this hellhole of peoples thoughts and feelings nobody but themselves care about.</p>
    `;
  };

  const createYap = () => {
    document.querySelector(".overlay").style.display = "flex";
    document.querySelector("#popupTitle").innerHTML = "Create Yap";
    document.querySelector("#popupContent").innerHTML = `
      <form class="createYapForm" id="createYapForm">
        <label for="yapContent">Yap:</label>
        <textarea id="yapContent" name="yapContent" maxlength="250" placeholder="Hey #Yapper ..."></textarea>
        <div class="char-counter"><span id="charCount">250</span> characters left</div>
        <button type="submit">Post</button>
      </form>
    `;

    setTimeout(() => {
      const form = document.getElementById("createYapForm");
      form.addEventListener("submit", handleCreateYap);

      const textarea = document.getElementById("yapContent");
      const charCountElement = document.getElementById("charCount");

      charCountElement.textContent = 250;

      textarea.addEventListener("input", () => {
        const remaining = 250 - textarea.value.length;
        charCountElement.textContent = remaining;

        if (remaining < 20) {
          charCountElement.style.color = "red";
        } else {
          charCountElement.style.color = "";
        }
      });
    }, 0);
  };

  const handleCreateYap = async (e) => {
    e.preventDefault();
    const content = document.getElementById("yapContent").value;
    const userId = parseInt(localStorage.getItem("userId"));

    if (!content.trim()) {
      alert("Yap content cannot be empty!");
      return;
    }

    if (!userId || isNaN(userId)) {
      alert("User ID is invalid. Please try logging in again.");
      return;
    }

    try {
      const response = await fetch("https://yapper-4qux.onrender.com/tweets", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          content: content.trim(),
          owner_id: userId
        })
      });

      if (response.ok) {
        closePopup();
        fetchTweets();
      } else {
        const errorData = await response.json();
        const errorMessage = typeof errorData.detail === 'string' 
          ? errorData.detail 
          : Array.isArray(errorData.detail)
            ? errorData.detail.map(err => err.msg).join(', ')
            : JSON.stringify(errorData);
        alert(`Failed to create yap: ${errorMessage}`);
      }
    } catch (error) {
      console.error("Error creating yap:", error);
      alert("Failed to create yap: Network error");
    }
  };

  const editYap = (yap) => {
    document.querySelector(".overlay").style.display = "flex";
    document.querySelector("#popupTitle").innerHTML = "Edit Yap";
    document.querySelector("#popupContent").innerHTML = `
      <form class="createYapForm" id="editYapForm">
        <label for="yapContent">Edit Yap:</label>
        <textarea id="yapContent" name="yapContent" maxlength="250">${yap.content}</textarea>
        <div class="char-counter"><span id="charCount">${250 - yap.content.length}</span> characters left</div>
        <button type="submit">Update Yap</button>
      </form>
    `;

    setTimeout(() => {
      const form = document.getElementById("editYapForm");
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        const content = document.getElementById("yapContent").value;
        handleEditYap(yap.id, content);
      });

      const textarea = document.getElementById("yapContent");
      const charCountElement = document.getElementById("charCount");

      // Update character count on input
      textarea.addEventListener("input", () => {
        const remaining = 250 - textarea.value.length;
        charCountElement.textContent = remaining;

        if (remaining < 20) {
          charCountElement.style.color = "red";
        } else {
          charCountElement.style.color = "";
        }
      });
    }, 0);
  };

  const handleEditYap = async (id, content) => {
    try {
      const response = await fetch(`https://yapper-4qux.onrender.com/tweets/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          content,
          owner_id: parseInt(localStorage.getItem("userId"))
        })
      });

      if (response.ok) {
        closePopup();
        fetchTweets();
      } else {
        alert('Failed to update yap');
      }
    } catch (error) {
      console.error('Error updating yap:', error);
      alert('Failed to update yap');
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    try {
      let endpoint = "https://yapper-4qux.onrender.com/tweets/search";
      const params = new URLSearchParams();

      //determine search type by prefix for tags
      if (searchQuery.startsWith("#")) {
        endpoint = "https://yapper-4qux.onrender.com/tweets/search/tags";
        params.append("tag", searchQuery.substring(1));
      } else if (searchQuery.startsWith("@")) { //search for user by @username
        endpoint = "https://yapper-4qux.onrender.com/users/search/";
        params.append("query", searchQuery.substring(1));
      } else {
        //regular tweet search
        params.append("query", searchQuery);
      }
      
      const response = await fetch(`${endpoint}?${params}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setTweets(data);
        console.log(data);
      };

    } catch (error) {
      console.error("Error searching tweets: ", error);
      
    };
  };

  const deleteYap = async (id) => {
    if (!window.confirm('Are you sure you want to delete this yap?')) {
      return;
    }
  
    try {
      const response = await fetch(`https://yapper-4qux.onrender.com/tweets/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
  
      if (response.ok) {
        fetchTweets(); // Refresh the tweets list
      } else {
        alert('Failed to delete yap');
      }
    } catch (error) {
      console.error('Error deleting yap:', error);
      alert('Failed to delete yap');
    }
  };

  const closePopup = () => {
    document.querySelector(".overlay").style.display = "none";
  };

  if (window.location.pathname === "/login") {
    const handleLogin = async (e) => {
      e.preventDefault();
      const username = document.getElementById("loginUsername").value;
      const password = document.getElementById("loginPassword").value;
      try {
        const formData = new FormData();
        formData.append("username", username);
        formData.append("password", password);
        const response = await fetch("https://yapper-4qux.onrender.com/auth/login", {
          method: "POST",
          body: formData,
        });
        if (response.ok) {
          const data = await response.json();
          console.log('Login response:', data); // Debug log
          if (!data.user_id) {
            alert("Server did not return user ID");
            return;
          }
          localStorage.setItem("token", data.access_token);
          localStorage.setItem("userId", data.user_id.toString()); // Ensure it's stored as string
          window.location.href = "/";
        } else {
          const errorData = await response.json();
          alert(`Login failed: ${errorData.detail || 'Invalid credentials'}`);
        }
      } catch (error) {
        console.error("Login error: ", error);
        alert("Login Failed, Server Error");
      }
    };
    return (
      <div className="App">
        <header>
          <h1>Yapper</h1>
        </header>
        <main>
          <h2 className="authTitle">Login to Yapper</h2>
          <form className="loginForm" onSubmit={handleLogin}>
            <div>
              <label htmlFor="loginUsername">Username:</label>
              <input
                type="text"
                id="loginUsername"
                name="loginUsername"
                required
              />
              <label htmlFor="loginPassword">Password:</label>
              <input
                type="password"
                id="loginPassword"
                name="loginPassword"
                required
              />
              <button type="submit">Login</button>
            </div>
          </form>
          <p className="logregText">
            Don't have an account? <a href="/register">Register</a>
          </p>
        </main>
      </div>
    );
  }
  if (window.location.pathname === "/register") {
    const handleRegister = async (e) => {
      e.preventDefault();
      const username = document.getElementById("registerUsername").value;
      const password = document.getElementById("registerPassword").value;
      const passwordRepeat = document.getElementById(
        "registerPasswordRepeat"
      ).value;
      if (password !== passwordRepeat) {
        alert("Passwords do not match!");
        return;
      }
      try {
        const response = await fetch("https://yapper-4qux.onrender.com/users", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ username, password }),
        });
        if (response.ok) {
          window.location.href = "/login";
        } else {
          alert("Registration failed!");
        }
      } catch (error) {
        console.error("Registration error: ", error);
        alert("Registration Failed, Server Error");
      }
    };
    return (
      <div className="App">
        <header>
          <h1>Yapper</h1>
        </header>
        <main>
          <h2 className="authTitle">Register a Yapper account</h2>
          <form className="registerForm" onSubmit={handleRegister}>
            <div>
              <label htmlFor="registerUsername">Username:</label>
              <input
                type="text"
                id="registerUsername"
                name="registerUsername"
              />
              <label htmlFor="registerPassword">Password:</label>
              <input
                type="password"
                id="registerPassword"
                name="registerPassword"
              />
              <label htmlFor="registerPasswordRepeat">Repeat password:</label>
              <input
                type="password"
                id="registerPasswordRepeat"
                name="registerPasswordRepeat"
              />
              <button type="submit">Register</button>
            </div>
          </form>
          <p className="logregText">
            Already have an account? <a href="/login">Login</a>
          </p>
        </main>
      </div>
    );
  }

  const handleLogout = () => {
    localStorage.removeItem("token");
    window.location.href = "/login";
  };

  if (localStorage.getItem("token")) {
    return (
      <div className="App">
        <div className="overlay">
          <div className="overlayCloser" onClick={closePopup}></div>
          <div className="popup">
            <div className="popupHeader">
              <h2 id="popupTitle"></h2>
              <button className="closePopup" title="Close" onClick={closePopup}>
                X
              </button>
            </div>
            <div id="popupContent"></div>
          </div>
        </div>
        <header>
          <h1>Yapper</h1>
          <div className="header-buttons">
            <button
              className="infoBtn"
              title="About Yapper"
              onClick={aboutYapper}
            >
              ?
            </button>
            <button className="logoutBtn" title="Logout" onClick={handleLogout}>
              X
            </button>
          </div>
        </header>
        <div className="action-area">
          <button className="createYap" onClick={createYap}>
            Create Yap
          </button>
          <div>
            <input 
              type="text" 
              placeholder="Search #tags or tweets..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}            
            />
            <button className="searchBtn" title="Search" onClick={handleSearch}>
              <img src={searchIcon} alt="search icon" />
            </button>
          </div>
        </div>
        <nav>
          <a href="/" className="pageSelected">
            Home
          </a>
        </nav>
        <main>
          {/* displays each yap in the object array */}
          {sortedYapps.map((yap) => (
            <div key={yap.id} className="yap">
              <div className="yap-header">
                <h2>@{yap.username || "unknown"}</h2>
                <p>
                  {new Date(yap.created_at).toLocaleString("en-GB", {
                    year: "numeric",
                    month: "2-digit",
                    day: "2-digit",
                    hour: "2-digit",
                    minute: "2-digit",
                    hour12: false,
                  })}
                </p>
              </div>
              <p>{yap.content}</p>
              {yap.owner_id === parseInt(localStorage.getItem("userId")) && (
                <>
                  <button className="editYap" onClick={() => editYap(yap)}>
                    Edit
                  </button>
                  <button className="deleteYap" onClick={() => deleteYap(yap.id)}>
                    Delete
                  </button>
                </>
              )}
            </div>
          ))}
        </main>
      </div>
    );
  }
}

export default App;
