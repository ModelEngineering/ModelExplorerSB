const SearchDisplay = ({results, setSelected}: {results: SearchResult[], setSelected: Function}) => {

  return results.length != 0 ?
      (<div id="search-result-container" className="glassmorphism">
        {results.map((result, index) => (
          <button 
            className="search-result" 
            key={result.id}
            style={index === 0 ? {borderTop: "0px"} : {}}
            onClick={() => setSelected(result)}
          >
            <p>{result.title}</p>
          </button>
        ))}
      </div>) : (<></>)
      
}


export default SearchDisplay;