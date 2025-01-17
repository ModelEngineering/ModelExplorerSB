import {
  BiDownload as DownloadIcon,
  BiChart as ChartIcon,
  BiTable as TableIcon,
} from "react-icons/bi";
import { DisplayMode } from "../visualization";

// This component displays the visualization sidebar, including buttons for changing the display mode and downloading project files
const VizSidebar = ({
  handleDownload,
  graphDisabled,
  tableDisabled,
  setDisplayMode,
}: {
  handleDownload: React.MouseEventHandler<HTMLButtonElement>;
  graphDisabled: boolean;
  tableDisabled: boolean;
  setDisplayMode: Function;
}) => {
  return (
    <div
      id="viz-sidebar"
      className="flex w-full flex-row justify-start gap-1 lg:h-full lg:w-fit lg:flex-col"
    >
      {/* Button for changing the display mode to graph */}
      <button
        className="h-8 w-8 rounded-t-lg bg-slate-700 bg-opacity-50 pl-2 text-center text-2xl hover:bg-opacity-70 lg:rounded-l-none lg:rounded-r-lg"
        title="View as Chart"
        disabled={graphDisabled}
        onClick={() => setDisplayMode(DisplayMode.Graph)}
      >
        <ChartIcon className="text-base" />
      </button>

      {/* Button for changing the display mode to table */}
      <button
        className="h-8 w-8 rounded-t-lg bg-slate-700 bg-opacity-50 pl-2 text-center text-2xl hover:bg-opacity-70 lg:rounded-l-none lg:rounded-r-lg"
        title="View as Table"
        disabled={tableDisabled}
        onClick={() => setDisplayMode(DisplayMode.Table)}
      >
        <TableIcon className="text-base" />
      </button>

      {/* Button for downloading project files */}
      <button
        className="h-8 w-8 rounded-t-lg bg-slate-700 bg-opacity-50 pl-2 text-center text-2xl hover:bg-opacity-70 lg:rounded-l-none lg:rounded-r-lg"
        title="Download Project Files as Zip"
        onClick={handleDownload}
      >
        <DownloadIcon className="text-base" />
      </button>
    </div>
  );
};

export default VizSidebar;