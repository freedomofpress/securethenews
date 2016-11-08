const Leaderboard = require('./leaderboard.js');
const Teaser = require('./teaser.js');
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

const $teaser = $('#teaser');

if ($teaser.length !== 0) {
  const teaser = new Teaser({
    el: $teaser,
  });
  teaser.render();
}
