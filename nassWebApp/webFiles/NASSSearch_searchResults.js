"use strict";
(function(NASSSearch){
	
	function SearchResults(nassMain)
	{
		this.nassMain = nassMain;
		this.subscribe("GUIfy_onDisplay", this.onDisplay.bind(this));
	}
	NASSSearch.SearchResults = SearchResults;
	SearchResults = GUIfyClass(SearchResults, "searchResults");
	SearchResults.prototype.onDisplay = function(disp)
	{
		if(disp)
		{
			//Fill the summary
			var summaryDOM = $.parseHTML("<div>JobID: " + this.nassMain.urlParams["jobid"] + "</div>")[0];
			summaryDOM.appendChild(this.nassMain.initData["search"].toDOM());
			this.GUIfyElement.children("summary").html(summaryDOM);
			
			//Begin to poll
			this.pollInterval = window.setInterval(this.poll.bind(this), 2000);
		}
	};
	SearchResults.prototype.poll = function()
	{
		var self = this;
		$.ajax("/api_searchPoll", {
			contentType : "application/json; charset=UTF-8",
			method : "POST",
			data : "{\"jobid\":\""+this.nassMain.urlParams["jobid"]+"\"}",
			processData : false
		})
		.done(function(data, status, jXHR){
			self.GUIfyElement.children("*[data-guify-name=progress]").children(".statusField").first().html(data);
			
			var firstData = data.split(" ")[0];
			if(firstData == "DONE" || firstData == "FAILED" || firstData == "CANCELLED")
				clearInterval(self.pollInterval);
		});
	};
	
	//Dummy placeholders (to get default GUIfy controllers on objects)
	function SearchResults_Summary()
	{
		
	};
	NASSSearch.SearchResults_Summary = GUIfyClass(SearchResults_Summary, "summary");
	
	function SearchResults_Progress()
	{
		
	};
	NASSSearch.SearchResults_Progress = GUIfyClass(SearchResults_Progress, "progress");
	
	function SearchResults_Results()
	{
		
	};
	NASSSearch.SearchResults_Results = GUIfyClass(SearchResults_Results, "results");
	
})(window.NASSSearch = window.NASSSearch || {});