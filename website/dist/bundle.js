/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ "./js/app.js":
/*!*******************!*\
  !*** ./js/app.js ***!
  \*******************/
/***/ (() => {

eval("// Remove import 'dotenv/config'\n// Instead, you can access environment variables via process.env if needed\n\n// Example usage (not directly in app.js):\n// console.log(process.env.MY_ENV_VARIABLE); // Assuming this variable is passed during the build\n\n// add classes for mobile navigation toggling\nvar CSbody = document.querySelector('body');\nvar CSnavbarMenu = document.querySelector('#cs-navigation');\nvar CShamburgerMenu = document.querySelector('#cs-navigation .cs-toggle');\nCShamburgerMenu.addEventListener('click', function () {\n  CShamburgerMenu.classList.toggle('cs-active');\n  CSnavbarMenu.classList.toggle('cs-active');\n  CSbody.classList.toggle('cs-open');\n  // run the function to check the aria-expanded value\n  ariaExpanded();\n});\n\n// checks the value of aria expanded on the cs-ul and changes it accordingly whether it is expanded or not\nfunction ariaExpanded() {\n  var csUL = document.querySelector('#cs-expanded');\n  var csExpanded = csUL.getAttribute('aria-expanded');\n  if (csExpanded === 'false') {\n    csUL.setAttribute('aria-expanded', 'true');\n  } else {\n    csUL.setAttribute('aria-expanded', 'false');\n  }\n}\n\n// mobile nav toggle code\nvar dropDowns = Array.from(document.querySelectorAll('#cs-navigation .cs-dropdown'));\nvar _loop = function _loop() {\n  var item = _dropDowns[_i];\n  var onClick = function onClick() {\n    item.classList.toggle('cs-active');\n  };\n  item.addEventListener('click', onClick);\n};\nfor (var _i = 0, _dropDowns = dropDowns; _i < _dropDowns.length; _i++) {\n  _loop();\n}\nvar faqItems = Array.from(document.querySelectorAll('.cs-faq-item'));\nvar _loop2 = function _loop2() {\n  var item = _faqItems[_i2];\n  var onClick = function onClick() {\n    item.classList.toggle('active');\n  };\n  item.addEventListener('click', onClick);\n};\nfor (var _i2 = 0, _faqItems = faqItems; _i2 < _faqItems.length; _i2++) {\n  _loop2();\n}\n\n// Get the video\nvar video = document.getElementById(\"myVideo\");\n\n// Get the button\nvar btn = document.getElementById(\"myBtn\");\n\n// Pause and play the video, and change the button text\nfunction myFunction() {\n  if (video.paused) {\n    video.play();\n    btn.innerHTML = \"Pause\";\n  } else {\n    video.pause();\n    btn.innerHTML = \"Play\";\n  }\n}\n\n// Copyright Current Year\n// Wait until the DOM is fully loaded\ndocument.addEventListener(\"DOMContentLoaded\", function () {\n  // Get the current year\n  var currentYear = new Date().getFullYear();\n\n  // Find the element with the id \"cs-copyright-year\"\n  var copyrightYearElement = document.getElementById(\"cs-copyright-year\");\n\n  // Check if the element exists\n  if (copyrightYearElement) {\n    // Set the text content to the current year\n    copyrightYearElement.textContent = currentYear;\n  }\n});\n\n//# sourceURL=webpack://_/./js/app.js?");

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module can't be inlined because the eval devtool is used.
/******/ 	var __webpack_exports__ = {};
/******/ 	__webpack_modules__["./js/app.js"]();
/******/ 	
/******/ })()
;