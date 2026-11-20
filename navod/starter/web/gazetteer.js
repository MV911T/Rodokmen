// Gazetteer for the origin map: places that appear in people's birth/death places.
// Coordinates are approximate (village centre, ±2 km). Add a place here when validate.js lists it as missing.
// a = aliases matched as substrings of b.place / d.place (longest match wins); off = outside the map frame.
window.RODOKMEN_GAZ = [
  { n: 'Brno', a: ['Brno'], lat: 49.195, lon: 16.61 },
  { n: 'Třebíč', a: ['Třebíč'], lat: 49.215, lon: 15.88 },
  { n: 'Jihlava', a: ['Jihlava'], lat: 49.4, lon: 15.59 }
];
