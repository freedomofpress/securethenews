const Leaderboard = require('./leaderboard.js');
const Teaser = require('./teaser.js');
const Backbone = require('backbone');
const _ = require('underscore');
const $ = require('jquery');

require('./styles/main.scss');

Backbone.$ = $;

const $leaderboard = $('#leaderboard');

if ($leaderboard.length !== 0) {
  const leaderboard = new Leaderboard(Object.assign({},
    $leaderboard.data(),
    { el: $leaderboard, }
  ));
  leaderboard.render();
}

const $teaser = $('#teaser');
if ($teaser.length !== 0) {
  const teaser = new Teaser({
    el: $teaser,
  });
  teaser.render();
}

$('.mobile-header-js').on('click', (event) => {
  $('.nav').addClass('uncollapsed transition');
  $('.tap-catcher-js').show();
});

$('.tap-catcher-js').on('touchend click', (e) => {
  const $nav = $('.nav');
  $nav.removeClass('uncollapsed');
  $nav.one('transitionend', () => {
    $nav.removeClass('transition')
  })
  // Delay the removal of the tap catcher so that the subsequently fired
  // click event is also caught. Typically this happens with a 300ms delay
  // after touchend.
  setTimeout(() => $('.tap-catcher-js').hide(), 350);
});
