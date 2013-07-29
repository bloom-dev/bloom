/*
 * @author Oakland J. Peters
 * @institution Laboratory of Dr. Dakshanamurthy, Lombardi Cancer Center, Georgetown Medical Center
 * @date started: ~01/01/2013
 * @requires jQuery.js v1.7.1
 */
/*
List of contained functions:
print_array()
get_keys()
get_property_vector()
 */



/*
 * ===== Debugging Functions =====
 */
function debug_display(message)	{
	/*
	//To activate Javascript console in Firefox:
	//	devtools.chrome.enabled: true
		devtools.debugger.remote-enabled: true
	*/
	var browser = determine_browser();		//opera,firefox,safari,chrome,ie
	if(window.DEBUG == true)	{
		switch(browser)	{
		case 'opera':
			break;
		case 'firefox':
			console.log(message);
			break;
		case 'safari':
			break;
		case 'chrome':
			javascript: console.log(message);	//Prints to Chrome console
			break;
		case 'ie':
			window.console && console.log(message);	//This has not been tested
			break;
		default:
			//do nothing
		}
	}
}
function activate_debugging()	{
	window.DEBUG = true;
	$("#topbar").css("background","#444");	//Change color of top bar as a sign that debugging has been activated.
	debug_display("<h1>Debugging activated</h1>");
	$.ajax({
		url:"ajax/get_session_id.php",
		datatype:'html',
		success:function(ses_id)	{
			debug_display("SESSION ID = "+ses_id);	
		}
	});
}
function deactivate_debugging()	{
	window.DEBUG = false;
	$("#debugging_text").html( "" );
}


/*
 * ===== Object & Array Manipulation =====
 */
function print_array(domObject,arrayObject)	{
	$(domObject).append( arrayObject.join('<br>') );
}
function get_keys(obj)	{
	//Get the keys of a javascript object 
	var keys = [];
	for (var k in obj)	keys.push(k);
	return keys;
}
function get_property_vector(obj,prop_name)	{
	var props = [];
	var keys = get_keys(obj);
	for (var key in obj)	{
		props.push(obj[key][prop_name]);
	}
	return props;
}
function object_string(in_obj)	{
	//Object may be an array of objects. Individual properties may not be arrays however (yet - this is easily changed)
	var obj_string = "";
	var obj =[];
	if( $.isArray(in_obj) == false)	{
		obj.push(in_obj);	
	}	else	{
		obj = in_obj;
	}
	obj_string="<br>";
	for (var i=0; i<obj.length; i++)	{		//Iterate through array entries of object
		obj_string += "Object["+i+"]={ ";
		for (var prop in obj[i])	{			//Iterate through properties of that entry in array
			obj_string += "("+prop+" : "+obj[i][prop]+"),";
		}
		obj_string += " }<br>";
	}
	return obj_string;
}


function contains(haystack,needle) {
	//Looks for 'value' inside 'Array'. 
 	//This is a replacement for some uses of .indexOf() - which doens't work in IE < 9.
	//Note: Underscore.js: _.contains(haystack,needle) does the same thing
	for (var i = 0; i < haystack.length; i++) {
		if (haystack[i] === needle) { return true; }
	}
	return false;
}



/*
 * 	==== String Support =====
 */


//----- str.format()
if (!String.prototype.format) {		//first, checks if it isn't implemented yet
	String.prototype.format = function() {
		/**
		 *  
		 *  String formatting function, in the style of Python's STRING.format().
		 *  Arguments are inserted into String, with '{i}' being replaced by arguments[i]. 
		 *  
		 *  Examples:
		 *  var mystr = "First name:{0}, Last name:{1}, Middle initial:{mid}, Rank:{3}";
		 *	mystr.format("John","Doe", ,"Executive",{'mid':'K.'})
		 *  >>> "First name:John, Last name:Doe, Middle initial:K., Rank:Executive"
		 */
		var args = Array.prototype.slice.call(arguments);		//Converts 'arguments' to a proper array
		var last_arg = args.slice(-1)[0];	//The final argument... because Javascript doesn't have a .last()/[-1] notation
		
		function replacer(match,content) {	//Replace with return value
			/**
			 * Returns a new value to replace the match. This function is used as argument into the String.replace(regex[,rep_func]) function
			 * match: full string '{X}'
			 * content: inside string: 'X'
			 */
			
			if (content % 1 == 0) {	//~if it is an integer (number or string) 
				return args[content]; 
			} else { 
				if (content in last_arg) { //If the last argument has property named by content, even if that property is inherited.
					if (last_arg[content] == undefined) {	//Do not throw an error
						return "-";							//But replace with nullstring/NA type of symbol
					} else {
						return last_arg[content];	//Replace with the property of last_arg
					}
				} else {
					return match;	//Make no change
				}
			}		
		}
		return this.replace(/{(.*?)}/g,replacer);
	}
}

// ----- str.capitalize()
if (!String.prototype.capitalize) {		//first, checks if it isn't implemented yet
	String.prototype.capitalize = function() {
		return this.replace(/\w\S*/g, function(text){
			return text.charAt(0).toUpperCase() + text.substr(1).toLowerCase();
		});
	}
}
function toTitleCase(str)
{
    return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}

/*
 * ===== Website Support =====
 */

function delete_cookies(substrings)	{
	/*
	 * Deletes all cookies containing any of the substrings contained in substrings[].
	 * substrings[] should be an array of strings, but can accept a single string.
	 * Updates functionality originally contained in the function deleteCookies()
	 */
	//Handle case of single (non-array) string passed in
	if ( Object.prototype.toString.call(substrings) !== '[object Array]')	{
		substrings = [].concat( substrings );
	}
	var cookies = document.cookie.split(";");
	//For each cookie and each substring			($.each() is a generic iterator provided by jQuery)
	$.each(cookies,function(cindex,cookie) {
		$.each(substrings,function(sindex,substring) {
			//var eqPos = cookie.indexOf("=");		//Array.indexOf() doesn't work in ie < 9
			var eqPos = $.inArray("=",cookie);		//$.inArray is a jQuery replacement for Array.indexOf(), which doesn't work in ie <9
	    	var name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
	    	//if (name.indexOf(substring) != -1)	{
	    	if ($.inArray(substring,name) != -1) { //$.inArray is a jQuery replacement for Array.indexOf(), which doesn't work in ie <9
	    	    document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
	    	}
		});
	});
}
function drop_cookies(cookie_names) {
	/**
	 * Delete all cookies in the array 'cookie_names'.
	 * 
	 * @uses: jquery-cookie.js		- $.removeCookie()
	 */
	$.each(cookie_names,function(ind,val){
		$.removeCookie(val);
	});
}
function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null;
}
function urlencode (str) {
	/**
	 * Encodes URL string, in the manner expected by PHP.
	 * Obtained from: https://github.com/kvz/phpjs
	 * Credit due to Philip Peterson, and those mentioned below:
	 */
	// http://kevin.vanzonneveld.net
	// +   original by: Philip Peterson
	// +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
	// +      input by: AJ
	// +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
	// +   improved by: Brett Zamir (http://brett-zamir.me)
	// +   bugfixed by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
	// +      input by: travc
	// +      input by: Brett Zamir (http://brett-zamir.me)
	// +   bugfixed by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
	// +   improved by: Lars Fischer
	// +      input by: Ratheous
	// +      reimplemented by: Brett Zamir (http://brett-zamir.me)
	// +   bugfixed by: Joris
	// +      reimplemented by: Brett Zamir (http://brett-zamir.me)
	// %          note 1: This reflects PHP 5.3/6.0+ behavior
	// %        note 2: Please be aware that this function expects to encode into UTF-8 encoded strings, as found on
	// %        note 2: pages served as UTF-8
	// *     example 1: urlencode('Kevin van Zonneveld!');
	// *     returns 1: 'Kevin+van+Zonneveld%21'
	// *     example 2: urlencode('http://kevin.vanzonneveld.net/');
	// *     returns 2: 'http%3A%2F%2Fkevin.vanzonneveld.net%2F'
	// *     example 3: urlencode('http://www.google.nl/search?q=php.js&ie=utf-8&oe=utf-8&aq=t&rls=com.ubuntu:en-US:unofficial&client=firefox-a');
	// *     returns 3: 'http%3A%2F%2Fwww.google.nl%2Fsearch%3Fq%3Dphp.js%26ie%3Dutf-8%26oe%3Dutf-8%26aq%3Dt%26rls%3Dcom.ubuntu%3Aen-US%3Aunofficial%26client%3Dfirefox-a'
	str = (str + '').toString();

	// Tilde should be allowed unescaped in future versions of PHP (as reflected below), but if you want to reflect current
	// PHP behavior, you would need to add ".replace(/~/g, '%7E');" to the following.
	return encodeURIComponent(str).replace(/!/g, '%21').replace(/'/g, '%27').replace(/\(/g, '%28').
	replace(/\)/g, '%29').replace(/\*/g, '%2A').replace(/%20/g, '+');
}
function urldecode (str) {
	/**
	 * Encodes URL string, in the manner expected by PHP.
	 * Obtained from: https://github.com/kvz/phpjs
	 * Credit due to Philip Peterson, and those mentioned below:
	 */
    // http://kevin.vanzonneveld.net
    // +   original by: Philip Peterson
    // +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
    // +      input by: AJ
    // +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
    // +   improved by: Brett Zamir (http://brett-zamir.me)
    // +      input by: travc
    // +      input by: Brett Zamir (http://brett-zamir.me)
    // +   bugfixed by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
    // +   improved by: Lars Fischer
    // +      input by: Ratheous
    // +   improved by: Orlando
    // +   reimplemented by: Brett Zamir (http://brett-zamir.me)
    // +      bugfixed by: Rob
    // +      input by: e-mike
    // +   improved by: Brett Zamir (http://brett-zamir.me)
    // +      input by: lovio
    // +   improved by: Brett Zamir (http://brett-zamir.me)
    // %        note 1: info on what encoding functions to use from: http://xkr.us/articles/javascript/encode-compare/
    // %        note 2: Please be aware that this function expects to decode from UTF-8 encoded strings, as found on
    // %        note 2: pages served as UTF-8
    // *     example 1: urldecode('Kevin+van+Zonneveld%21');
    // *     returns 1: 'Kevin van Zonneveld!'
    // *     example 2: urldecode('http%3A%2F%2Fkevin.vanzonneveld.net%2F');
    // *     returns 2: 'http://kevin.vanzonneveld.net/'
    // *     example 3: urldecode('http%3A%2F%2Fwww.google.nl%2Fsearch%3Fq%3Dphp.js%26ie%3Dutf-8%26oe%3Dutf-8%26aq%3Dt%26rls%3Dcom.ubuntu%3Aen-US%3Aunofficial%26client%3Dfirefox-a');
    // *     returns 3: 'http://www.google.nl/search?q=php.js&ie=utf-8&oe=utf-8&aq=t&rls=com.ubuntu:en-US:unofficial&client=firefox-a'
    // *     example 4: urldecode('%E5%A5%BD%3_4');
    // *     returns 4: '\u597d%3_4'
    return decodeURIComponent((str + '').replace(/%(?![\da-f]{2})/gi, function () {
        // PHP tolerates poorly formed escape sequences
        return '%25';
    }).replace(/\+/g, '%20'));
}

function pluginEnabled(name) {
    var plugins = navigator.plugins,
        i = plugins.length,
        regExp = new RegExp(name, 'i');
    while (i--) {
        if (regExp.test(plugins[i].name))	{
        	//console.log(String(i) +":  "+ plugins[i].name);
        	return true;
        }
    }
    return false;
}
function determine_browser()	{
	//var isOpera = !!window.opera || navigator.userAgent.indexOf('Opera') >= 0;
	var isOpera = !!window.opera || $.inArray('Opera',navigator.userAgent) >= 0;	//$.inArray is a jQuery replacement for Array.indexOf(), which doesn't work in ie <9
    // Opera 8.0+ (UA detection to detect Blink/v8-powered Opera)
	var isFirefox = typeof InstallTrigger !== 'undefined';   // Firefox 1.0+
	//var isSafari = Object.prototype.toString.call(window.HTMLElement).indexOf('Constructor') > 0;
	var isSafari = $.inArray('Constructor',Object.prototype.toString.call(window.HTMLElement)) > 0;	//$.inArray is a jQuery replacement for Array.indexOf(), which doesn't work in ie <9
	    // At least Safari 3+: "[object HTMLElementConstructor]"
	var isChrome = !!window.chrome;                          // Chrome 1+
	var isIE = /*@cc_on!@*/false;                            // At least IE6
	if (isOpera)	{ return 'opera';	}
	if (isFirefox) { return 'firefox'; }
	if (isSafari) { return 'safari'; }
	if (isChrome) { return 'chrome'; }
	if (isIE) { return 'ie'; }
} 

/*
 * ===== HTML/CSS Box Model Manipulation =====
 */
function resize_to(target,css_name,relative,resize_percent)	{
	/* Sets $css_name, of $target, to $resize_percent of $relative's $css_name.
	 * $target,$relative	: result of jQuery selector.
	 * $css_name			: string of css trait. So far only test for 'height' or 'width'
	 * $resize_percent		: decimal number.
	 */
	/*
	 * 	//target and relative should be results of jquery selectors.
		//Example #1:
		resize_to($("#structural_drawing_visualization>iframe"),'height',$("body"),0.33)
		//Example #2:
		var target = $("#structural_drawing_visualization>iframe");
		var css_name = 'height';
		var relative = $("body");
		var resize_percent = 0.33;
		resize_to(target,css_name,relative,resize_percent);
		resize_to( $("#structural_drawing_visualization>iframe"), 'height', $("body"), 0.33 );
	*/
		var relative_string = relative.css(css_name);		//css_name might be 'height' or 'width'
		var relative_number = Math.round( relative_string.substring(0,relative_string.indexOf("px")));
		var target_number = Math.round( relative_number * resize_percent );
		var target_string = String(target_number) + "px";
		target.css(css_name,target_string);
}

//
//======== Sizing Class
//
//@todo: Add ability to get height/width in percent.
//	Perhaps: Sizing.prototype.percent('height')
//	Or: Sizing.prototype.get('height')
//
//var parent = new Sizing( this.ref.parent() );
//var ratio = this.height / parent.height 

function Sizing (jquery_ref) {
	//Used to get & set sizes of HTML block elements (often nested).
	//Depends on jQuery.
	//I should amend this to also track the size units (px,%, etc)
	//To find it's units, look for '%','px', etc.  (build a seperate function for this)
	//	via: s.indexOf("%") !== -1
	
	this.ref = jquery_ref;
	this.id = jquery_ref.attr('id');
	this.allowed = ["height","width"];		//allowed attributes
	this.set_allowed();
}
Sizing.prototype.set_allowed=function() {
	for (i in this.allowed) {
		var temp = this.ref.css(this.allowed[i]); //get CSS value
		if (temp) { //~if temp is defined
			if (temp.slice(-2) == 'px') {	//Cut off units 'px', if present
				temp = parseInt(temp);
			}
			this[this.allowed[i]] = temp;	//Set property = css
		}
	}
}
function set_css(css_name,new_value) {
	//Ex. var iframe = new Sizing($("iframe.cobweb")); 
	//iframe.set('width',parent.width*0.9)
	this.ref.css(css_name,new_value);
}

Sizing.prototype.set=function(css_name,new_value) {
	this.set_allowed();
	//if (this.allowed.indexOf(css_name) > -1)	{	//If css_name is in allowed
	//If css_name is in allowed
	if ($.inArray(css_name,this.allowed) > -1) {	//$.inArray is a jQuery replacement for Array.indexOf(), which doesn't work in ie <9
		this.ref.css(css_name,new_value);
	} else	{
		//Do nothing
	}
}




/*
 * ===== XML Support =====
 */
function fetch_xml(xml_url) {
	/** Retreives an XML file from URL input via jQuery AJAX, and translates to a JS array.
	 *  XML-attributes will be lost.
	 *  
	 *  Requires: jQuery.js:		$.ajax(), .find(), .each(), $.extend()
	 *  		  utility.js: 	.format(),debug_display()
	 * 
	 *  Example:
	 *  var xmlObj = {};
	 *  fetch_xml("./config_vars.xml").success(function(xmlDoc) {
	 *  	var root = $(xmlDoc).contents();
	 *  	xmlObj = parse_xml( root );
	 *  });		
	 */

	return	$.ajax({
				type:"GET",
				url:xml_url,
				dataType:"xml",
				async: false,
				error: function(ajaxErr) {
					debug_display("Cannot access XML document at: {0}, because of error: {1}.".format(xml_url,AjaxErr));
					throw "Cannot access XML document at: {0}, because of error: {1}.".format(xml_url,AjaxErr);
				}
			});
}
function parse_xml(node) {
	/**
	 * Recursively deconstruct XML object, into a simpler Javascript object.
	 * parse_xml() is designed to be used with fetch_xml(). See that function for documentation.
	 */
	var xmlObj = {};
	var node_name = node[0].tagName;
	xmlObj[node_name] = {};
	
	if (node[0].childElementCount == 0) {	//If no children --> this is a leaf/data node
		xmlObj[node_name] = node[0].textContent;
	} else {	//This has children
		$(node).find(">").each(function(){
			$.extend(xmlObj[node_name], parse_xml($(this)));	//~Array.push()
		});
	}
	return xmlObj;
}



/*
 * ===== Misc =====
 */
function check_json_length(obj,maxlength)	{
	//maxlength in paramter is optional 
	maxlength = (typeof maxlength === "undefined") ? 1800 : maxlength;
	string_obj = JSON.stringify(obj);
	if (string_obj.length > maxlength)	{
		debug_display('Object over max length of '+String(maxlength)+'<br>');
		debug_display('Object = '+string_obj+'<br>');
		return true;
	}
	else	{
		return false;	//The object is 'Ok' 
	}
}







/*
 * ===== In Development =====
 */

/*
var xmlObj = {};
fetch_xml("./config_vars.xml").success(function(xmlDoc) {			
	var root = $(xmlDoc).contents();
	xmlObj = parse_xml( root );
});
*/



function check(in_variable,category_type,category_data)	{
	/** Used in error checking. 
	 *  Intended to imitate functionality in Python class Category, and decorators @ check, and @ confirm.
	 *  This function is basically a stub, intended to be filled in later.
	 */
		switch (str.toLowerCase(category_type))	{
			case "enumerated":
				return in_variable in category_data;
			default:
				debug_display('Error in call to check( '+in_variable+", "+category_type+", "+category_data+" )");
		}
}
//@deprecated:
/*
function set_default(in_variable,default_value)	{
	//Used for setting default values for input arguments of other functions.
	//Equivalent to:   in_variable = typeof in_variable !== 'undefined' ? in_variable : default_value;
	if (typeof in_variable !== 'undefined')	{
		return a
	} else	{
		return default_value
	}
}
function start_php_session()	{
	//This function presently unused
	$.ajax({
		url:"./ajax/get_session_id.php",
		datatype:'text',
		success:function(idstring){
			//idstring should be automatically set as a cookie named "PHPSESSID" 
		},
		error:function(err_text) {
			debug_display("Could not get PHP session id.");
		}
	});
}
*/
