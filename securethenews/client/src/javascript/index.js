const Leaderboard = require('./leaderboard.js');
const Backbone = require('backbone');
const $ = require('jquery');

Backbone.$ = $;

const $leaderboard = $('#leaderboard');

if ($leaderboard.length !== 0) {
  const leaderboard = new Leaderboard({
    el: $leaderboard,
  });
  leaderboard.render();
}
