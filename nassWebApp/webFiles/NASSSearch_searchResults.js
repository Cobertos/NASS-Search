"use strict";
(function(NASSSearch){
	
	function SearchResults(thisGUI, nassMain)
	{
		//This handles the other side of the NASSSearch web tool
		//Upon clicking the button an event is generated from the searchVisual and complimenting components.
		//Control is handed to the search handler with a jobId and we do this
		//Control can also come here if the page is provided a jobId directly
		//We change the default page a bit
		//Poll the search
		//etc
	}
	NASSSearch.SearchResults = SearchResults;
	
	
})(window.NASSSearch = window.NASSSearch || {});