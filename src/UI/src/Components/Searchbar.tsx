import { useState } from "react"
import { useLunr } from 'react-lunr'
import json from '../Assets/context.json'
import lunr from "lunr"
import { BiSearchAlt as SearchIcon } from "react-icons/bi"

const data = json;
interface SearchResult {
  title: string | null,
  abstract: string,
  runid: string,
  id: number
}
const store : Record<string, SearchResult> = {};
const index = lunr(function () {
  this.field("title");
  this.field("abstract");
  this.ref("id");
  this.metadataWhitelist = ['position']

  for (let entry = 0; entry < data.length; entry++) {
    this.add({
      title: data[entry].title,
      abstract: data[entry].abstract,
      id: entry
    });

    store[entry] = {
      title: data[entry].title,
      abstract: data[entry].abstract,
      // project_id: data[entry].project_id,
      runid: data[entry].runid,
      id: entry
    };
  }
});

const Searchbar = ({setResult}: {setResult(value:string): void}) => {
  const [query, setQuery] = useState("");
  const results = useLunr(query, index, store) as SearchResult[];
  
  return (
    <div id="searchbar" className="flex-col">
      <div id="searchbar-input-container" className="flex-row small-searchbar" >
        <SearchIcon id="search-icon" />
        <input id="searchbar-input" className="small-searchbar" placeholder="Search..." onChange={(event) => setQuery(event.target.value)}/>
      </div>
      {results.length != 0 ?
        (<div id="search-result-container">
          {results.map((result, index) => (
            <button 
              className="search-result" 
              key={result.id}
              style={index === results.length - 1 ? {borderBottom: "0px"} : {}}
              onClick={() => setResult(result.runid)}
            >
              <p>{result.title}</p>
            </button>
          ))}
        </div>) : (<></>)
      }
    </div>
  )
}

export default Searchbar;
