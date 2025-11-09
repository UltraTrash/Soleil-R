import React, { useState, useEffect } from "react";
import starfield from './starfield1.jpg';
import './App.css';

// so that we can switch between local and deployed backend easily
const API_BASE_URL = process.env.REACT_APP_API_URL || "https://soleiljs.onrender.com";

function App() {
  const [cme, setCme] = useState(null);
  const [flare, setFlare] = useState(null);
  const [gst, setGst] = useState(null);
  const [ips, setIps] = useState(null);

  // Helper to fetch an event type
  const fetchEvent = async (endpoint, setState) => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/events/${endpoint}`);
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
