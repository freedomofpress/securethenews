const Leaderboard = require('./leaderboard.js');
const Backbone = require('backbone');
const $ = require('jquery');
const _ = require('underscore');

Backbone.$ = $;

// Without this, we get "Uncaught ReferenceError: jQuery is not defined" in jquery.floatThead.js
// TODO use browserify-shim?
// https://github.com/substack/node-browserify/issues/868#issuecomment-54295447
global.jQuery = require("jquery");
const floatThead = require('floatthead');

const $leaderboard = $('#leaderboard');

if ($leaderboard.length !== 0) {
  const leaderboard = new Leaderboard({
    el: $leaderboard,
  });
  leaderboard.render();

  // Get initial offset of leaderboard thead from top
  let theadTop = $('div.leaderboard table thead').offset().top;

  // Float the leaderboard table header when the user scrolls past it.
  $(window).scroll(_.debounce(function() {
    let leaderboardTable = $('div.leaderboard table');
    if ($(this).scrollTop() > theadTop) {
      leaderboardTable.floatThead();
    } else {
      leaderboardTable.floatThead('destroy');
    }
  }, 10));

  // When the Backbone view is re-rendered, the table gets replaced in the DOM
  // and we lose the old floated thead. Re-float (if scrolled) when the view
  // changes.
  leaderboard.on('render', function() {
    let leaderboardTable = $('div.leaderboard table');
    if ($(window).scrollTop() > theadTop) {
      leaderboardTable.floatThead();
    }
  });
}
