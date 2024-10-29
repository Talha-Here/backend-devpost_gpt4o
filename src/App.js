// import React from 'react';
// import CaptionExtractor from './summarizer';

// function App() {
//   return (
//     <div>
//       <CaptionExtractor />
//     </div>
//   );
// }

// export default App;

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import CaptionExtractor from './summarizer';
import IdeaDetails from './IdeaDetails'; // Assuming you created SearchResult component

function App() {
  return (
    <Routes>
      <Route path="/" element={<CaptionExtractor />} />
      <Route path="/idea-details" element={<IdeaDetails />} />
    </Routes>
  );
}

export default App;
