import Leaderboard from './leaderboard'
import Teaser from './teaser'
import Backbone from 'backbone'
import _ from 'underscore'
import $ from 'jquery'

import './styles/main.scss'


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

$('#show-more').on('click', (event) => {
  if ($('#show-more-categories').hasClass('d-hidden')) {
    $('#show-more-categories').removeClass('d-hidden');
    $('#show-more span').html('Show less');
  } else {
    $('#show-more-categories').addClass('d-hidden');
    $('#show-more span').html('Show more');
  }
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
