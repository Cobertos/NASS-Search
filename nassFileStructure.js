"use strict";

function isDef(o)
{
	return !(typeof o === "undefined" || o === null);
}
function isFunc(o)
{
	return typeof o === "function";
}
function isArray(o)
{
	return Object.prototype.toString.call(o) === "[object Array]";
}

(function(sasTools){

//Formatting functionality
function pad(n, width) {
  n = n + "";
  return n.length >= width ? n : new Array(width - n.length + 1).join("0") + n;
}	
sasTools.format = {"BYTES":0, "TEXT":1, "INT":2};
sasTools.formatData = function(bytes, format)
{
	var s="";
	for(var i=0; i<bytes.length; i++)
	{
		if(format === sasTools.format.BYTES)
			s += pad(bytes[i].toString(16), 2);
		else if(format === sasTools.format.TEXT)
			s += String.fromCharCode(bytes[i]);
		else if(format === sasTools.format.INT)
			bytes[i] = pad(bytes[i].toString(16), 2);
	}
	if(format === sasTools.format.INT)
	{
		s = parseInt(bytes.reverse().join(""), 16);
	}
	return s;
};
sasTools.formatBytes = function(s)
{
	var newS = "";
	for(var i=0; i<s.length; i+=2)
	{
		if(i > 0) //Nothing on first iteration
		{
			if(((i/2) % 8) === 0) //Every 8 bytes
				newS += "<br>";
			else if(((i/2) % 4) === 0) //Every 4 bytes
				newS += "&nbsp;&nbsp;";
			else //Every byte
				newS += "&nbsp;";
		}
		newS += s.substr(i,2);
	}
	return newS;
}

//Reading data from the byte array
sasTools.readField = function(bytes, byteOffset, field, mapObj)
{
	//Get the position and length
	var readBytes = [];
	var pos = isFunc(field.pos) ? field.pos(mapObj) : field.pos;
	var len = isFunc(field.len) ? field.len(mapObj) : field.len;
	if(typeof pos === "number")
		pos = [pos];
		
	//Actually read the field
	for(var p=0; p<pos.length; p++)
	{
		//Safety check
		if((pos[p] + len) > bytes.length)
			return null;
		
		var readBytesInner = [];
		for(var i=pos[p]+byteOffset; i<pos[p]+byteOffset+len; i++)
			readBytesInner.push(bytes[i]);
		readBytes.push(readBytesInner);
	}
	
	//Format the field in two ways:
	//Val as bytes, val as formatted
	var output = {};
	output.compare = {"match":true, "output":""};
	output.byteVal = [];
	output.formatVal = [];
	for(var i=0; i<readBytes.length; i++)
	{
		var bVal = sasTools.formatData(readBytes[i].slice(0), sasTools.format.BYTES);
		output.byteVal.push(bVal);
		//Val as it's actual value, formatted
		var fVal = sasTools.formatData(readBytes[i].slice(0), field.format); 
		fVal = field.format === sasTools.format.BYTES ? sasTools.formatBytes(fVal) : fVal;
		output.formatVal.push(fVal);
		
		//Check val against what it should be according to the spec
		var comp = field.compare({"byteVal":bVal, "formatVal":fVal}, mapObj);
		output.compare.match = output.compare.match && comp.match;
		output.compare.output = comp.output; //TODO, consolidate this somehow
	}
	return output;
}
sasTools.readBitmap = function(bytes, offset, map)
{
	//Go through all the fields in a bitmap
	var objMapped = {};
	for(var i=0; i<map.length; i++)
	{
		var field = map[i];
		
		//Get the value of the field
		var output = sasTools.readField(bytes, offset, field, objMapped);
		
		//Debug info
		var s = "<tr style=\"background-color:" + (output.compare.match ? "#AAFFAA" : "#FFAAAA") + ";\">";
		s +=    "<td>" + field.field + "</td>";
		s +=    "<td>" + field.pos + "</td>"
		s +=    "<td>" + field.len + "</td>"
		s +=    "<td>[" + output.byteVal.join(",<br>") + "]</td>"
		s +=    "<td>[" + output.formatVal.join(",<br>") + "]</td>"
		s +=    "<td>" + output.compare.output + "</td></tr>";
		$("#outputReport").append(s);
	}
	return objMapped;
}

//Bitmaps that map to the database files
//Field - Name of field
//Pos - A scalar, array, or function that returns scalar or array with pos(es) of field
//Len - A scalar, or function that returns scalar with len of field
//Format - The format the value takes if transformed from bytes
//Compare - Compares byte string to expected value and set a variable on mapObj if needed

//


function defaultCompare(val, mapObj){ return {"match":true, "output":""}; }
sasTools.dbHeaderBitmap = [
{"field":"Magic Number",
"pos":0,"len":32,"format":sasTools.format.BYTES,
"compare":function(val,mapObj)
{
	var match = (val.byteVal === "000000000000000000000000c2ea8160b31411cfbd92080009c7318c181f1011");
	var output = match ? "Matched" : "Did not match";
	mapObj.magicMatch = match;
	return {"match":match, "output":output};
}},
{"field":"Align 2",
"pos":32,"len":1,"format":sasTools.format.BYTES,
"compare":function(val,mapObj)
{
	var output = (val.byteVal==="33" ? "Align" : "No align");
	mapObj.align2 = (val.byteVal==="33");
	return {"match":true, "output":output};
}},
{"field":"Align 1",
"pos":35,"len":1,"format":sasTools.format.BYTES,
"compare":function(val,mapObj)
{
	var output = (val.byteVal==="33" ? "Align" : "No align");
	mapObj.align1 = (val.byteVal==="33");
	return {"match":true, "output":output};
}},
{"field":"Endianness",
"pos":37,"len":1,"format":sasTools.format.BYTES,
"compare":function(val,mapObj)
{
	var output = (val.byteVal==="01" ? "Little [Intel]" : "Big");
	mapObj.bigEndian = (val.byteVal==="01");
	return {"match":true, "output":output};
}},
{"field":"Dataset Name",
"pos":92,"len":64,"format":sasTools.format.TEXT,
"compare":function(val,mapObj)
{
	mapObj.name = val.formatVal;
	return {"match":true, "output":""};
}},
{"field":"Header Length",
"pos":196,"len":4,"format":sasTools.format.INT,
"compare":defaultCompare},
{"field":"Page Size",
"pos":200,"len":4,"format":sasTools.format.INT,
"compare":function(val,mapObj)
{
	mapObj.pageSize = val.formatVal;
	return {"match":true, "output":""};
}},
{"field":"Page Count",
"pos":204,"len":4,"format":sasTools.format.INT,
"compare":function(val,mapObj)
{
	mapObj.pageCount = val.formatVal;
	return {"match":true, "output":""};
}}
];

sasTools.pageBitmap = [
{"field":"Page Type",
"pos":16,"len":2,"format":sasTools.format.BYTES,
"compare":function(val,mapObj)
{
	//Lookup table for page types. Little Endian
	var t = {"0000":"meta", "0001":"data", "0002":"mix", "0004":"amd", "0080":"meta", "0090":"comp"};
	var match = isDef(t[val.byteVal]);
	var output = "Type: " + t[val.byteVal];
	mapObj.type = t[val.byteVal];
	return {"match":match, "output":output};
}},
{"field":"Data Block Count",
"pos":18,"len":2,"format":sasTools.format.INT,
"compare":function(val,mapObj)
{
	return {"match":true, "output":""};
}},
{"field":"Subheader Pointer Count",
"pos":20,"len":2,"format":sasTools.format.INT,
"compare":function(val,mapObj)
{
	mapObj.SHPC = val.formatVal;
	return {"match":true, "output":""};
}},
{"field":"Subheader Pointers",
"pos":function(mapObj){var a = []; for(var i=0; i<mapObj.SHPC; i++){a.push(22+i*12);} return a;},"len":12,"format":sasTools.format.BYTES,
"compare":function(val,mapObj)
{
	mapObj.SHPs = mapObj.SHPs || [];
	mapObj.SHPs.push(val.byteVal);
	return {"match":true, "output":""};
}},

/*
oset length conf. description
B+8+SC*SL DL medium if NRD>0, 8 byte alignment; DL = (B+8+SC*SL+7) % 8 *
8
B+8+SC*SL+DLRC*`RL` medium SAS7BDAT packed binary data data row count := RC =
(BC-SC)
C %`PL` medium subheader data and/or ller; C =
(B+8+SC*SL+DL+RC*RL)*/
];

sasTools.subheaderPointerBitmap = [
{"field":"Subheader Offset",
"pos":0,"len":4,"format":sasTools.format.INT,
"compare":defaultCompare},
{"field":"Subheader Length",
"pos":4,"len":4,"format":sasTools.format.INT,
"compare":defaultCompare},
{"field":"Subheader Compression",
"pos":8,"len":1,"format":sasTools.format.BYTES,
"compare":defaultCompare},
{"field":"Subheader Type",
"pos":9,"len":1,"format":sasTools.format.BYTES,
"compare":defaultCompare},
];
/*
0 4j8 high int, oset from page start to subheader
4j8 4j8 high int, length of subheader := QL
8j16 1 medium int, compression := COMP
9j17 1 low int, subheader type := ST
10j18 2j6*/

/*sasTools.subheaderTypeRowBitmap = [
{"field":"Subheader Offset",
"pos":0,"len":4,"format":sasTools.format.INT,
"compare":defaultCompare},
{"field":"Subheader Offset",
"pos":0,"len":4,"format":sasTools.format.INT,
"compare":defaultCompare},
{"field":"Subheader Offset",
"pos":0,"len":4,"format":sasTools.format.INT,
"compare":defaultCompare},
{"field":"Subheader Offset",
"pos":0,"len":4,"format":sasTools.format.INT,
"compare":defaultCompare},
{"field":"Subheader Offset",
"pos":0,"len":4,"format":sasTools.format.INT,
"compare":defaultCompare},
{"field":"Subheader Offset",
"pos":0,"len":4,"format":sasTools.format.INT,
"compare":defaultCompare},
{"field":"Subheader Offset",
"pos":0,"len":4,"format":sasTools.format.INT,
"compare":defaultCompare},
{"field":"Subheader Offset",
"pos":0,"len":4,"format":sasTools.format.INT,
"compare":defaultCompare},*/
];

})(window.sasTools = window.sasTools || {});