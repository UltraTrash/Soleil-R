/* import starfield from './starfield1.jpg';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={starfield} className="App-starfield" alt="starfield" />
        <h1>Welcome to Soleil!</h1>
        <h2>Soleil is the web application you need to monitor outer space's various weather phenomena</h2>

        <div className="space-weather-grid">

        <div class="phenomenon1">
          <h3>Coronal Mass Ejection</h3>
          <div className="coronal-mass-ejection"></div>
          <img class="image1" src="images/coronal_mass_ejection_image.png" alt="cme_image"></img>
        </div>

        <div className="solar-flares"></div>

        <div className="geomagnetic-storms"></div>

        <div className="interplanetary-shocks"></div>
        </div>

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
export default App; */

import React, { useState, useEffect } from "react";
import starfield from './starfield1.jpg';
import './App.css';

function App() {
  const [cme, setCme] = useState(null);
  const [flare, setFlare] = useState(null);
  const [gst, setGst] = useState(null);
  const [ips, setIps] = useState(null);

  // Helper to fetch an event type
  const fetchEvent = async (endpoint, setState) => {
    try {
      const res = await fetch(`http://127.0.0.1:5000/api/events/${endpoint}`);
      if (!res.ok) throw new Error("Network response was not ok");
      const data = await res.json();
      setState(data);
    } catch (err) {
      console.error(`Failed to fetch ${endpoint}:`, err);
    }
  };

  useEffect(() => {
    fetchEvent("getcme", setCme);
    fetchEvent("getflr", setFlare);
    fetchEvent("getgst", setGst);
    fetchEvent("getips", setIps);
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <img src={starfield} className="App-starfield" alt="starfield" />
        <h1>Welcome to Soleil!</h1>
        <h2>Soleil is the web application you need to monitor outer space's various weather phenomena</h2>

        <div className="space-weather-grid">

          <div className="coronal-mass-ejection">
            {cme ? (
              <>
                <h3>Coronal Mass Ejection (CME)</h3>
                <p>Time: {cme.eventTime}</p>
                <p>Source: {cme.sourceLocation || "N/A"}</p>
              </>
            ) : <p>Loading...</p>}
          </div>

          <div className="solar-flares">
            {flare ? (
              <>
                <h3>Solar Flare (FLR)</h3>
                <p>Time: {flare.eventTime}</p>
                <p>Class: {flare.classType || "N/A"}</p>
              </>
            ) : <p>Loading...</p>}
          </div>

          <div className="geomagnetic-storms">
            {gst ? (
              <>
                <h3>Geomagnetic Storm (GST)</h3>
                <p>Time: {gst.eventTime}</p>
                <p>Link: {gst.link ? <a href={gst.link} target="_blank" rel="noreferrer">{gst.link}</a> : "N/A"}</p>
              </>
            ) : <p>Loading...</p>}
          </div>

          <div className="interplanetary-shocks">
            {ips ? (
              <>
                <h3>Interplanetary Shock (IPS)</h3>
                <p>Time: {ips.eventTime}</p>
                <p>Location: {ips.location || "N/A"}</p>
              </>
            ) : <p>Loading...</p>}
          </div>

        </div>
      </header>
    </div>
  );
}

export default App;
