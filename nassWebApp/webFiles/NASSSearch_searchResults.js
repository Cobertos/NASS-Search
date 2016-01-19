"use strict";
(function(NASSSearch){
	
	function SearchResults(nassMain)
	{
		this.nassMain = nassMain;
		this.resultsTable = this.GUIfyChild
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
			var jsonData = JSON.parse(data);
			
			console.log(jsonData);
			
			var status = jsonData[0];
			var firstWord = status.split(" ")[0];
			if(firstWord == "DONE")
			{
				var cases = jsonData[1];
				self.children("progress")[0].updateStatus("STATUS: " + status);
				for(var i=0; i<cases.length; i++)
				{
					var currCase = cases[i];
					var c = currCase[0];
					var link = currCase[1];
					self.children("results")[0].addResult(c, link);
				}
			}
			else
			{
				var caseCount = jsonData[1];
				self.children("progress")[0].updateStatus("STATUS: " + status + "| CASECOUNT: " + caseCount);
			}
			
			if(firstWord == "DONE" || firstWord == "FAILED" || firstWord == "CANCELLED")
				clearInterval(self.pollInterval);
			
		});
	};
	
	//Dummy placeholders (to get default GUIfy controllers on objects)
	function SearchResults_Summary()
	{
		
	};
	SearchResults_Summary = GUIfyClass(SearchResults_Summary, "summary");
	
	function SearchResults_Progress()
	{
		this.jStatusEl = this.GUIfyElement.children(".statusField").first();
	};
	SearchResults_Progress = GUIfyClass(SearchResults_Progress, "progress");
	SearchResults_Progress.prototype.updateStatus = function(statusStr)
	{
		this.jStatusEl.html(statusStr);
	};
	
	function SearchResults_Results()
	{
		this.jDisplayTableEl = this.GUIfyElement.children("table").first();
		//TODO: Add button to get more cases this.moreButton = this.GUIfyElement.children(".
		this.clearResults();
	};
	SearchResults_Results = GUIfyClass(SearchResults_Results, "results");
	SearchResults_Results.prototype._resultInit = function()
	{
		var initRow = "<tr>"
		+ "<td>YEAR</td>"
		+ "<td>CASE #</td>"
		+ "<td>PSU</td>"
		+ "<td>View in case viewer</td>"
		+ "</tr>";
		this.jDisplayTableEl.html(initRow);
	};
	SearchResults_Results.prototype.addResult = function(resCase, resLink)
	{
		var resLinkAbv = resLink;
		if(resLink.length > 20)
			resLinkAbv = "..." + resLink.substr(resLink.length-20,20);
		
		var newRow = "<tr>"
		+ "<td>" + resCase["CASE_YEAR"] + "</td>"
		+ "<td>" + resCase["CASENO"] + "</td>"
		+ "<td>" + resCase["PSU"] + "</td>"
		+ "<td><a href=\"" + resLink + "\">" + resLinkAbv + "</a></td>"
		+ "</tr>";
		this.jDisplayTableEl.append(newRow);
	};
	SearchResults_Results.prototype.clearResults = function()
	{
		this.jDisplayTableEl.empty();
		this._resultInit();
	};
	
})(window.NASSSearch = window.NASSSearch || {});