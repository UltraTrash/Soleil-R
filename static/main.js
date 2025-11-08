const baseTransforms = {
  background: 'translateZ(-10px) scale(2)',
  foreground: 'translateZ(-5px) scale(1.5)'
};

function initInfiniteParallax() {
  const layers = [
    { key: 'background', element: document.querySelector('.background'), speed: 0.2 },
    { key: 'foreground', element: document.querySelector('.foreground'), speed: 0.5 }
  ];

  layers.forEach(layer => {
    const clone = layer.element.cloneNode(true);
    layer.element.parentElement.appendChild(clone);
    layer.clone = clone;
  });

  function update() {
    const scrollY = document.querySelector('.wrapper').scrollTop;
    const h = window.innerHeight;

    layers.forEach(layer => {
      const offset = (scrollY * layer.speed) % h;

      const base = baseTransforms[layer.key];

      layer.element.style.transform =
        `${base} translateY(${offset}px)`;

      layer.clone.style.transform =
        `${base} translateY(${offset - h}px)`;
    });

    requestAnimationFrame(update);
  }

  update();
}

initInfiniteParallax()

async function fetchEvents(page = 0) {
  const response = await fetch(`/api/events?page=${page}`);
  const events = await response.json();
  return events;
}
