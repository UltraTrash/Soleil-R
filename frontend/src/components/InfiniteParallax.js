import React from "react";
import "./InfiniteParallax.css";

const InfiniteParallax = () => {
  return (
    <div className="parallax-container">
      {/* Background layer */}
      <div className="parallax-layer background"></div>
      {/* Foreground layer */}
      <div className="parallax-layer foreground"></div>
      <div className="content">
        <h1>Infinite Space Parallax</h1>
        <p>Scroll down forever...</p>
      </div>
    </div>
  );
};

export default InfiniteParallax;