const SearchDisplay = ({
  display,
  results,
  setSelected,
}: {
  display: boolean;
  results: Context[];
  setSelected: Function;
}) => {
  return results.length != 0 ? (
    <div
      id="search-result-container"
      className={display ? "glassmorphism" : "display-none"}
    >
      {results.map((result, index) => (
        <button
          className="search-result"
          key={result.runid}
          style={index === 0 ? { borderTop: "0px" } : {}}
          onClick={() => setSelected(result)}
        >
          <p>{result.title}</p>
        </button>
      ))}
    </div>
  ) : (
    <></>
  );
};

export default SearchDisplay;
