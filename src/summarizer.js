import React, { useState } from 'react';
import axios from 'axios';

import './styles.css'; // Adjust the path if your styles.css is in a different folder
import LoadingSpinner from './LoadingSpinner'; // Import the loading spinner

import ReactMarkdown from 'react-markdown';

// import IdeaDetails from './IdeaDetails';

// import { useHistory } from 'react-router-dom';
// import { useNavigate } from 'react-router-dom';

const CaptionExtractor = () => {
  const [videoUrl, setVideoUrl] = useState('');
  const [captions, setCaptions] = useState('');
  const [error, setError] = useState('');
  const [summary, setSummary] = useState('');
  const [google_search_ideas, setGoogleSearchIdeas] = useState('');
  const [keywords, setKeywords] = useState('');
  const [loading, setLoading] = useState(false); // Loading state

  // const history = useHistory();
  // const navigate = useNavigate();
  // const handleSearchIdeaClick = (idea) => {
  //   console.log('Selected idea:', idea);
  //   navigate('/idea-details', { state: { idea } }); // Pass the idea in state
  // };

  const handleSearchIdeaClick = (idea) => {
    console.log('Selected idea:', idea);
    const url = '/idea-details'; // This is your route
    const params = new URLSearchParams({ idea }).toString(); // Convert idea to a query string
    window.open(`${url}?${params}`, '_blank'); // Open in a new tab
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setCaptions('');
    setSummary('');
    setGoogleSearchIdeas('');
    setKeywords('');
    setLoading(true); // Start loading

    try {
      const response = await axios.post(
        'http://127.0.0.1:5000/flask_app/extract-captions',
        { video_url: videoUrl },
      );

      setCaptions(response.data.captions);
      setSummary(response.data.summary);
      setGoogleSearchIdeas(response.data.google_search_ideas);
      setKeywords(response.data.main_keywords);
    } catch (err) {
      console.error('Error details:', err); // Logs the full error object to the console
      setError(err.response?.data?.error || 'An error occurred');
    } finally {
      setLoading(false); // Stop loading
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <div className="video-input-container common-container">
        <h1>VIDEO WEB</h1>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Enter YouTube Video URL"
            value={videoUrl}
            onChange={(e) => setVideoUrl(e.target.value)}
            required
          />
          <button type="submit">Extract Captions</button>
        </form>
        {error && <p style={{ color: 'red' }}>{error}</p>}
      </div>
      {loading && <LoadingSpinner />} {/* Line added to show loading spinner */}
      {summary && (
        <div className="summary-box common-container">
          <h2>Generated Summary:</h2>
          {/* <p>{summary}</p> */}
          <ReactMarkdown>{summary}</ReactMarkdown>
        </div>
      )}
      {google_search_ideas && (
        <div className="search-ideas common-container">
          <h2>Let LLM Search For You On Google?</h2>
          <ul>
            {google_search_ideas.map((idea, index) => (
              <li key={index}>
                <button onClick={() => handleSearchIdeaClick(idea)}>
                  {idea}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
      {keywords && (
        <div className="topic-keywords-container common-container">
          <h2 className="topic-keywords-heading">Topic Keywords</h2>
          <div className="topic-keywords">
            {keywords.map((keyword, index) => (
              <span key={index} className="topic-keyword">
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}
      {captions && (
        <div className="captions-box common-container">
          <h2>Transcript Of Video:</h2>
          <p>
            {captions.split('. ').map((sentence, index) => (
              <span key={index}>
                {sentence.trim()}.
                <br /> {/* Adding a line break after each sentence */}
              </span>
            ))}
          </p>
        </div>
      )}
    </div>
  );
};

export default CaptionExtractor;
