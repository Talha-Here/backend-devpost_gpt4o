import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';
import './IdeaDetails.css';
import ReactMarkdown from 'react-markdown';

const IdeaDetails = () => {
  const location = useLocation();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const queryParams = new URLSearchParams(location.search);
  const idea = queryParams.get('idea');

  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('Fetching data for idea:', idea);
        const response = await axios.post('http://127.0.0.1:8000/search', {
          query: idea,
        });
        setData(response.data);
      } catch (err) {
        setError(err.response?.data?.error || 'An error occurred');

        // Try accessing different keys to capture the error message
        // const errorMessage =
        //   err.response?.data?.error || err.message || 'An error occurred';
        // setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    if (idea) fetchData();
  }, [idea]);

  if (loading) return <p>Loading...</p>;
  if (error) return <p className="error-message">{error}</p>;

  return (
    <div className="idea-details-container">
      <h3 className="heading3">Google Search Summary</h3>

      <h2>Search : {idea}</h2>

      <p className="google-summary">
        <h4 className="heading4"> Reference URL</h4>
        <ul className="link-list link-list-reference">
          <a href={data?.url} target="_blank" rel="noopener noreferrer">
            {data?.url}
          </a>
        </ul>
        <ReactMarkdown>{data?.google_search_summary}</ReactMarkdown>
      </p>
      {/* <p>Primary URL: {data?.url}</p> */}

      <p>
        <h4 className="heading4"> Read More On Google</h4>

        <ul className="link-list">
          {data?.extracted_links.map((link, index) => (
            <li key={index}>
              <a href={link} target="_blank" rel="noopener noreferrer">
                {link}
              </a>
            </li>
          ))}
        </ul>
      </p>
    </div>
  );
};

export default IdeaDetails;
