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

$('.mobile-header-js').on('touchstart click', (event) => {
  $('.nav').addClass('uncollapsed');
  $('.tap-catcher-js').show();
});

$('.tap-catcher-js').on('touchend click', (e) => {
  $('.nav').removeClass('uncollapsed');
  // Delay the removal of the tap catcher so that the subsequently fired
  // click event is also caught. Typically this happens with a 300ms delay
  // after touchend.
  setTimeout(() => $('.tap-catcher-js').hide(), 350);
});
