/*
 * @author Oakland J. Peters
 * @date-started: ~07/01/2013 
 * @requires jQuery.js v1.10.1
 * @requires utility.js			: 
 */

if (window.console) { console.log('Loaded meta.js'); }

/* ====== To Do: =====
 * [] Test: potentially done functions.
 *   [] _check
 *   [] _for()
 *   [] _loop()
 * [] Test: _is() and other functions discern Object VS Array correctly.
 * 		Complication: when I wrote most of meta.js I was thinking that Arrays were NOT objects
 * 		... which is untrue in Javascript. (my brain was thinking Dict VS List in Python)
 * 
 * [] New Functions: Add:
 *   [] _match		~regex tester on strings, should return an array of matching groups
 *   [] _assert 	~ _check, but provides text information when not true.
 * 				Ex. _assert('function')(args[0]); //arg[0] to {caller_function} is not a function.
 *   [] _freeze(func,*args) //see notes below -- it's complicated
 *   			This is actually low-priority, and probably already implemented by underscore.js
 *   
 * [] Functionality: for _is() & _check() - allow arrays of categories - which are chained.
 * 				Ex. _is('defined','string')
 * 		[] Related: _has() should support arrays of properties. 
 * [] Functionality: _complain/_cry - to pass in Exception objects, to display more appropriately.
 * [] Advanced: _is() nesting. Requires parsing category string. Example:
 * 				Ex. _is('array[string]')	? maybe ?	 _is('array of strings')
 * 		~~>
 * 		return (function _nested_is() {
 * 			if (_is('array') {
 * 				jQuery.each(
 * 			}
 * 		});
 * [] Advanced: way to nest _loop()/_for() calls
 * [] Improve: the object equality test in _find() (for _is('object')(container) )
 * 
 * [] Look at list of functions here which resemble underscore.js functions
 * 		[] _has()--> _.has() 
 * 		probably: _for, _loop	resemble 	_.invoke(), _.map()
 *    [] _.pluck() -- the common use case from collections:
 *    		_.pluck(stooges, 'name');	=> ["moe", "larry", "curly"]
 */



/*
 * Various examples: (more goals for syntax than currently working examples)
 * Ex #1:
 *  if ( all( _is
 * 	if ( all( _for(var1,var2,var3)(_is('defined')) ) ) { }
 *  if ( all( _for({name1:var1,name2:var2})(_is('string')) ) ) { }
 *  if ( all( _loop(_is('defined'))(var1,var2,var3) )) { }
 */


/* =================== Function Parameter Processing =====================
 * 
 * ============================================
 */
function _default(arg,default_value) {
	/**
	 *	Syntactic sugar for setting default function argument values in Javascript.
	 *	If no 'default_value' provided - uses 'null'.
	 *  Ex.
	 *	function myFunction(in_arg_1,in_arg_2) {
	 *		in_arg_1 = _default(in_arg_1,'Default value');
	 *		in_arg_2 = _default(in_arg_2,other_function_results());
	 *	}
	 */
	if (typeof default_value === 'undefined') { default_value = null; }
	return (typeof arg !== 'undefined' ? arg : default_value);
}
function _required() {
	var args = Array.prototype.slice.call(arguments);	//Make arguments a normal array
	
	//If only one argument, and if that argument as an array--> treat arg[0] as entire input arguments
	//Ex. _required([var1,var2,var3]) ~~> _required(var1,var2,var3)
	if (args.length == 1)	{
		if (args[0] instanceof Array) {
			args = args[0];			
		}
	}
	
	var any_undefined= any(args,function(elm){
		return (typeof elm === "undefined")?(true):(false);
	});
	if (any_undefined) {
		_debug("Invalid arguments to: ", arguments.callee.caller.name);
		return false;
	} else {
		return true;
	}
}
function _extract() {
	/**
	 * Utility function. Returns arguments as an array. 
	 * If only one array/object argument, extracts it's contents and returns.
	 * If only one argument is passed in, and that object is an array or object
	 * it's elements are extracted/'flatten' into a larger array, and returned.
	 * Implements a task I've done repeatetdly for meta.js functions.
	 * 
	 * function _newmeta() {
	 * 		var args = _extract(arguments);
	 * }
	 * _newmeta(['val1','val2'])	// args = ['val1','val2']
	 * _newmeta({name:'john',job:'programmer'})		//args = [{name:'john'},job:'programmer'}]
	 */
	var args = Array.prototype.slice.call(arguments);
	//try{
		if (args.length == 1) {		//Ex if [array] or {obj} passed in --> make them into entire arguments Array
			if( _is('array')(args[0]) ) {
				args = args[0];
				
			} else if ( _is('object')(args[0]) ) {
				var accumulator = [];
				jQuery.each(args[0],function(key,value)	{
					var temp = {};
					temp[key] = value;
					accumulator.push(temp);
				});
				args = accumulator;				
			}
		}
	//catch (err) {
	//	throw err;
	//}
	return args;
}

/* ===================  Cross-Browser Debug and Error Console Display =========================
 * 
 * ============================================
 */
function _debug() {
	/**
	 * Attempt to display debug information on the console.
	 * Only if window.DEBUG == true
	 * 
	 */
	if (window.DEBUG) {
		var args = Array.prototype.slice.call(arguments);
		var len = args.length;
		window.args = args;
		try {
			//If only 1 argument, and it is an array or object --> treat arg[0] as entire input arguments
			//Ex. _debug([var1,var2,var3])  ~~> _debug(var1,var2,var3)
			//Or. _debug({p1:var1,p2:var2}) ~~> _debug(
			if (args.length == 1) {	
				if ( _is('array')(args[0]) ) {
					args = arguments[0];
					len = args.length;
				} else if (_is('object')(args[0]) ) {
					args = arguments[0];		//the object no longer has a length
					len = Object.keys(args).length;	//now it has a length
				}
			}

			if(window.console){		//in IE - window.console invalid if console is not open.
				if(_is("string")(args[0])) {	//~first argument is string (~message parameter)
					var message = args.shift();		//extract first argument
				} else {
					var message = "# properties = "+len;
				}
				if(len < 10) 	{ console.group(message); } 
				else 			{ console.groupCollapsed(message); }
				
				
				jQuery.each(args,function(index,arg){	
					if (_is("number")(index)){		//Array indexes are numbers --> do not show them
						console.dirxml(arg);
					} else if (_is("string")(index) ) {		//~implies arg is an object
						//console.groupCollapsed(index);
						console.dirxml(arg); 
						//console.groupEnd();
					} else {		//Display as a string
						console.debug(index,arg);
					}
				});
				console.groupEnd();
				console.groupEnd();
			}
		} catch (err) {
			//Do nothing
			//Such as when calling _debug() in IE when console is not open
			throw err;
			alert("in _debug's catch.");
		}
	}
}
function _complain() {	
	/**
	 * Customized error-like function, optionally displaying the stack.
	 * Similar to _complain(), except (1) displays regardless of window.DEBUG,
	 * (2) uses console.error() instaed of console.debug()
	 * (3) if no console, falls back to throw Error().
	 */
	
	if (window.DEBUG != true) {
		return;		//do nothing
	}
	var args = Array.prototype.slice.call(arguments);

	
	try {
		if(_is("string")(args[0])) {	//~first argument is string (~message parameter)
			var message = args.shift();		//extract first argument
		} else {
			var message = ""
		}
		console.group();
		console.warn("An issue encountered in function '{0}', {1}".format(arguments.callee.caller.name,message));
		//console.trace();
		
		if(args.length >= 1) {
			console.group("Relevant variables: ");
			_debug(args);	//Display all remaining arguments
		}
		
		console.groupEnd();
	} catch (err) {			//Fallback condition - such as browser has no console
		//do nothing
	}
}
function _cry() {
	/**
	 * Customized error-like function, optionally displaying the stack.
	 * Similar to _complain(), except (1) displays regardless of window.DEBUG,
	 * (2) uses console.error() instaed of console.debug()
	 * (3) if no console, falls back to throw Error(). 
	 * 
	 */
	var args = Array.prototype.slice.call(arguments);
	if(_is("string")(args[0])) {	//~first argument is string (~message parameter)
		var message = args.shift();		//extract first argument
	} else {
		var message = ""
	}
	if (_is('undefined')(window.console))	{	//Fallback condition - such as browser has no console
		throw Error("Couldn't make standard _cry() error report. Non-standard report is: In function '{0}', {1}".format(arguments.callee.caller.name,message));
		return
	}

	console.group();
	console.error("In function '{0}', {1}".format(arguments.callee.caller.name,message));
	
	if(args.length >= 1) {
		console.group("Relevant variables: ");
		_debug(args);	//Display all remaining arguments
	}	
	console.groupEnd();
}

/* ===================Category- and Type- Checking=========================
 * 
 * ============================================
 */

function _is(category,options) {
	/**		_is(category[,options])(variable)
	 * Returns a Boolean function accepting a single input variable.
	 * Intended as syntactic sugar for creating commonly used anonymous functions.
	 * Closely related functions: _check, _convert. 
	 * 
	 * Examples:
	 * (1)  if (_is('defined')(myVar)
	 * (2)	if (any(my_array,_is('undefined'))) 	{ }
	 * (3)	if ( _is('enumerated',['yes','no'])(myVar) ) 	{ }
	 */
	category = _default(category,"");
	options = _default(options);
	var category_to_function = {
		"defined":function _defined(obj) 		{ return (typeof obj !== "undefined") ? true : false; },
		"undefined":function _undefined(obj) 	{ return (typeof obj === "undefined") ? true : false; },
		"enumerated":function _enumerated(obj) 	{ return contains(options,obj); },	//options~enumerated possibilities
		"string":function _string(obj)			{ return (typeof(obj)==="string"); },
		"number":function _number(obj)			{ return (typeof(obj)==="number"); },
		"array":function _array(obj) 			{ return (jQuery.isArray(obj)); },
		"object":function _object(obj)			{ return (typeof(obj)==="object"); },
		"function":function _function(obj) 		{ return (typeof(obj)==="function");},
		"boolean":function _boolean(obj)		{ return (typeof(obj)==="boolean");},
		"empty":function _empty(obj)			{ return ((obj.length==0) || (jQuery.isEmptyObject(obj))); }
	};
	/*//New, unfinished contents & ideas:
		"empty":function _empty				//null,[],{},""
		"iterable":		//array,object
		"float":
		"integer":
		"int":
		"url":
	*/
	
	//If no category provided
	if (category == "") {
		return _is.categories;
	}
	
	var func = category_to_function[ category.toLowerCase() ];
	//func.name = category;
	return func;
}
//Valid categories
_is.categories = ["defined","undefined","enumerated","string","number","array","object","function"];

function _assert(){
	/**	_assert(category[,options])(obj)
	 * 	_assert(boolean_function)(obj)
	 *  _assert(category)(obj)
	 *  
	 * Throws errors if 'obj' does not satisfy 'category'.
	 * Newer replacement for _check. Acts more like _is().
	 * 
	 */
	var args = Array.prototype.slice.call(arguments);
	var category = args[0];
	var options = _default(args[1]);
	
	if (_is('function')(category)) {
		var bool_func = category;
	} else {
		var bool_func = _is.call(null,category,options);
	}
	
	
	var func = (function _assertion(obj){
		if(!bool_func(obj)) {
			_complain("Variable does not satisfy: "+bool_func.name,obj);
		}
	});
	return func;
}
_check = _assert;							//Alias
_assert.categories = _is.categories;		//Valid categories - _check() directly calls _is(), so has same valid categories



/* =================== Container and Searching =========================
 * 
 * ============================================
 */

function _find(container)	{
	/**
	 * Finds key/index of elements in a container. Container can be array, object, or string.
	 * Related to _in(container). As with many meta.js functions, this actuall returns a function.
	 * 
	 * Example:
	 * _find(['a','b','c','d','a','e'])('a')
	 */
	//.... actually.... making _find() the primary function, and _is() simply call it
	//key = _find(container)(elm)
	//if key is a number or string, and not null or undefined.
	//	return true
	//else return false
	if (_is('string')(container)) {
		return (function _find_substring(elm){
			var accumulator = [];
			for (var i = 0; i < container.length; i++) {
				if (container.slice(i,i+elm.length) === elm) { accumulator.push(i); }
			}
			return accumulator;
		});
	}
	else if (_is('array')(container) ) {
		return (function _find_array_elm(elm){
			var accumulator = [];
			for (var i = 0; i < container.length; i++) {				
				if (container[i] === elm) { accumulator.push(i); }
			}
			return accumulator;
		});
	} else if (_is('object')(container)) {
		return (function _find_object_prop_val(elm){
			var accumulator = [];
			jQuery.each(container,function(key,value){
				if (value==elm) {	accumulator.push(key);		}
			});
			return accumulator;
		});
		
	} else {
		_cry("I don't know what to do with container. It should be a string, array, or object: ",container);
	}
}
_find.categories = ['string','array','object'];

function _in(container)	{
	/**
	 * 
	 *  Related to _find(container), except returns boolean.
	 *  ~__contains__(self,other) in Python - or 'elm in container'
	 *  
	 *  If 'container' is an Object:	_in(obj)(value)	Looks for VALUE in an object, not a KEY (~property name)
	 *  If 'container' is an Array:		_in(array)(string)	Checks if ENTIRE string == some element of array
	 *  	Thus _in(['ab'])('a')		returns false
	 *  If 'container' is a String: 	_in(string)(substring) Looks for SUBSTRING, in STRING. (not regex)
	 */
	/*
	if (_is('string')(container)) {
		var func = (function _in_string(elm) {
			var result = _find(container)(elm);
			if (_is('empty')(result)) {
				return false;
			} else {
				return true;
			}
		});
	} else if (_is('array')(container)) {
		var func = (function _in_array(elm) {
			var result = _find(container)(elm);
			if (_is('empty')(result)) {
				return false;
			} else {
				return true;
			}
		});
	} else if (_is('object')(container)) {
		var func = (function _in_object(elm) {
			var result = _find(container)(elm);
			if (_is('empty')(result)) {
				return false;
			} else {
				return true;
			}
		});
	} else {
		_cry("I don't know what to do with container. It should be a string, array, or object: ",container);
	}
	
	//func.name = "_in_string";
	return func;
	*/
	
	if (_is('string')(container)) {
		return (function _in_string(elm) {
			var result = _find(container)(elm);
			if (_is('empty')(result)) {
				return false;
			} else {
				return true;
			}
		});
	} else if (_is('array')(container)) {
		return (function _in_array(elm) {
			var result = _find(container)(elm);
			if (_is('empty')(result)) {
				return false;
			} else {
				return true;
			}
		});
	} else if (_is('object')(container)) {
		return (function _in_object(elm) {
			var result = _find(container)(elm);
			if (_is('empty')(result)) {
				return false;
			} else {
				return true;
			}
		});
	} else {
		_cry("I don't know what to do with container. It should be a string, array, or object: ",container);
	}
	_cry("You should never see this error.");
}
_in.categories = _find.categories;			//Since _in() directly calls _find()



/* =================== Misc Functions - Replicated By Undscore.js =========================
 * Since these are found in Underscore.js - I will probably remove them.
 * 
 * ============================================
 */
function _has(property) {
	/**	_has(prop)(obj)
	 * Returns a function to ask whether an object has a property.
	 * 
	 * Example:
	 * var myObj = {'name':'john',job:'president'}; prop='name';
	 * _has(prop)(myObj)		//Alternative to Javascripts if(prop in myObj)
	 */
	try {
		return (prop in obj) ? true : false;
	} catch(err) {		
		if (err.name == "TypeError") {	
			return false;		//May occur if obj undefined or null
		} else {
			throw err;
		}
	}
}
function _for(container,loop_type) {
	/**	_for(container[,loop_type='value'])(callback)
	 * 	_for(container)(callback)
	 * Loops across elements of a container.
	 * _for(obj)(callback)   ~~  for (elm in obj) {callback(elm);}
	 * 
	 * 'container' may be an array or object -- strings are treated a single element arrays.
	 * 'loop_type' is optional - refers to the values passed into callback. Defaults to 'values'
	 * 		Valid: 'values','keys','items'
	 * 
	 * Example:
	 * _for(['a','b','c'])(console.log)
	 * _for(['defined','string'])(_is)
	 * var myNumbers = _for([1,2,3])(function(elm){ return elm*2; })
	 * 
	 * ???meaingful/correct-->	_loop(_for(['defined','string'])(_is))(myVar)	???
	 */
	loop_type = _default(loop_type,'values');
	//_assert("enumerated",["values","keys","items"])(loop_type)
	
	//Do not loop across characters in a string ---> makes _for() play well with single inputs.
	if (_is('string')(container)) {	container = [container];	}
	if ( !_is('object')(container) ) {
		_cry("I'm confused in _for() by type of container.",container);
	}
	
	
	return (function _for_loop(element) {
		if(_is('array')(container)) {
			var accumulator = [];
		} else if (_is('object')(container)) {
			var accumulator = {};
		}
		
		jQuery.each(container,function(index,value){
			if (loop_type=="items") { 
				//element.apply(value,[index,value]); 
				result = element.call(value,index,value);
			} else if (loop_type=="values") {
				//element.apply(value,value);
				result = element.call(value,value);
			} else if (loop_type=="keys") {
				//element.apply(value,index);
				result = element.call(value,index);
			}
			
			if(_is('array')(container)) {
				accumulator.push(result);
			} else if (_is('object')(container)) {
				accumulator[index] = value;
			}
		}); 
		console.log(typeof(container),typeof(accumulator));
		return accumulator;
	});
}


function _loop(callbacks)	{
	/**
	 * Very similar to _for(), but returns a function which
	 * applies all functions in 'callbacks' (which can be an object, array, or a single function).
	 * 
	 * Returns an array bearing the results of each function.
	 * 
	 * Example:
	 * _loop(myFunctions)(obj)		~~>  myFunctions[0](obj), myFunctions[1](obj)
	 */
	
	//If callbacks is a single function
	if (_is('function')(callbacks)) {		
		return (function _loop_call(){ 
			return [callbacks.apply(callbacks,arguments)]; 
			});
		
	
	} else if (_is('array')(callbacks) || _is('object')(callbacks)) {
		
		return (function _loop_call(){
			var accumulator = [];
			var result = [];
			jQuery.each(callbacks,function(index,element){
				if (_is('function')(element)) {		//'element' is a subfunction in 'callbacks'
					result = element.apply(element,arguments) ;
				} else {
					result = undefined;
				}
				accumulator.push(result);
			});
			return accumulator;
		});
	} else {
		_complain("_loop doesn't know how to iterate or call 'callbacks'==",callbacks);
	}
}
function _select() {
	//Underscore.js	-->		_.pluck()
	
	/**
	 * Allows you to get the properties from an array of objects - with potentially dissimilar properties
	 * 
	 * Example:
	 * var employeeSelector = _select([{first:'John',last:'Doe'},{first:'Jane',job:'programmer'}]);
	 * employeeSelector('first')	//--> ['John','Jane']
	 * employeeSelector('job')	//--> [null,'programmer']
	 * 
	 * if (any((_select(myColl)(attr)),_is('function'))) {
	 */
	
}
function _filter(){
	//Undscore.js	-->		_.filter()
	
	/**
	 * Filters an array, or an object, for elements meeting only a certain property
	 */
}

/* =================== In-Development =========================
 * 
 * ============================================
 */



/* =================== In-Development =========================
 * 
 * ============================================
 */


function _convertible(category,options) {
	/**	_convertible(category,[options])
	 *  _convertible(category,[options])(obj)
	 *  
	 * Determines whether (obj) can be correctly converted to (category).
	 * Returns a Boolean function for a single input.
	 * ~sugar for: return _is(category)(_convert(category)(obj))  
	 */
}
//Valid categories - should be the intersection of _is.categories && _convert.categories
_convertible.categories = [];

//~alias: _cast
function _convert(category,options) {
	//Close relative of _is()
	//But requires seperate code
	
	/**
	 * Returns a function to convert an input object/array/primitive into a category.
	 */
}
_convert.categories = [];

function _pick() {
//Allows you to grab multiple elements out of a container, via an array of indexes/keys

//_pick("this is a big long sentence with an abrupt")([0,1,2,4,6,8])
//returns: ['t','h','i',' ',s','a'] 
	
}




function _slow_log(){
	/*
	 * Used when window.console not available, to record logging information in another
	 * window property (window.metajs_log_record). Intended to be accessed either:
	 * (1) when window.console becomes available (ex. IE8+, when user opens window.console)
	 * (2) alternate fashions - such as when manually debugging in browsers without a console.
	 *  
	 * Levels:
	 * 	DEBUG/_debug,COMPLAIN/_complain,CRY/_cry
	 * 
	 */
	try	{
		var args = Array.prototype.slice.call(arguments);
		if (!window.metajs_log_record) {
			window.metajs_log_record = [];
		}
		
		
	} catch (err) {
		_cry("Problems in _slow_log().",err);
	}
}

function _freeze() {
	/**		_freeze(func,args)
	 * [] Function.prototype.frozen = function(*args) { _freeze(this,*args); }
	 *   ... once the _frozen(func,args)/_partial(func,args) function is working 
	 *     [] ?? Deep semantics ??
	 *       Function.prototype.frozen_map(argIndex,container) {};
	 *       ... allows chaining:
	 *       multiply.frozen_map(0,[4,5]).frozen_map(1,[2,3])	//-->[[4*2,5*2],[4*3,5*3]]
	 *       Sugar:	multiply.frozen_map([4,5],[2,3])
	 *       ?? How to handle Super-Maps consideration of 'paired' VS 'product' variables?
	 *       	function complicated(a,b,c,d,e,f)
	 *       	multiply.frozen_map([0,2],[a1,a2],[c1,c2])		: .frozen_map(arg1,arg2,arg3)
	 *       	~~> the 1st and 3rd arguments are paired.	(everything in a single such .frozen_map is considered paired
	 *       		Note 1: length(arg1) must == number of (arg2,arg3,...)
	 *       		Note 2: length(arg2) should == length(arg3) etc.
	 */
	/* RELATED:
	 * [] Function.prototype.map = function(container) {
	 * 		var self = this;
	 * 		jQuery.each(container,function(index,value){
	 * 			self
	 * 		});
	 * }
	 */

	try	{
		var args = Array.prototype.slice.call(arguments);
		var func = args.shift();
		//Format for args should be:
		//	frozen arguments should have values in that argument position.
		//	All frozen arguments will be iterated across - so arguments which are not to be iterated
		//		on should be wrapped in Array brackets.
		//	unfrozen arguments should be undefined
		
		
		
	} catch (err) {
		throw err;
	}
}

function _lines(in_string) {
	return in_string.split("\n");
}

function _keys(obj) {
	//Convience function. Inferior to underscore.js's _.keys(obj)
   var keys = [];
   for(var key in obj){
      keys.push(key);
   }
   return keys;
}