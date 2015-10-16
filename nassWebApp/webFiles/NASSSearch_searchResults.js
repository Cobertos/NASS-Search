"use strict";
(function(NASSSearch){
	
	function SearchResults(thisGUI, nassMain)
	{
		this.thisGUI = thisGUI;
		this.nassMain = nassMain;
	}
	NASSSearch.SearchResults = SearchResults;
	SearchResults.prototype.init = function()
	{
		//Fill the summary
		var summaryDOM = $.parseHTML("<div>JobID: " + this.nassMain.urlParams["jobid"] + "</div>")[0];
		summaryDOM.appendChild(this.nassMain.initData["search"].toDOM());
		this.thisGUI.getChild("summary").html(summaryDOM);
		
		//Begin to poll
		this.pollInterval = window.setInterval(this.poll.bind(this), 2000);
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
			self.thisGUI.getChild("progress").children(".statusField").first().html(data);
		});
	};
	
})(window.NASSSearch = window.NASSSearch || {});