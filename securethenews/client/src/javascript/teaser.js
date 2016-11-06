const Backbone = require('backbone');
const _ = require('underscore');
const $ = require('jquery');
const Sites = require('./sites.js');
const template = require('./teasertemplate.jade');

const TEASER_SAMPLE_SIZE = 3;
const TEASER_REFRESH_INTERVAL = 5000;

module.exports = Backbone.View.extend({

  initialize() {
    // Instantiate collection using data injected into the template server-side
    this.collection = new Sites(window.STNsiteData);

    // Model to hold the current state of the leaderboard controls
    this.state = new Backbone.Model({
      teaserSites: new Sites(),
    });

    // Initial set of random sites
    this.randomizeTeaser();

    // Re-render the view whenever anything changes
    this.listenTo(this.state, 'change', this.render);

    // Start periodically refreshing the set of random sites in the teaser
    this.startRandomizingTeaser();

    // Pause the periodic refresh when the user hovers over the teaser, and
    // resume when they move the cursor away.
    this.$el.hover(this.stopRandomizingTeaser.bind(this),
                   this.startRandomizingTeaser.bind(this));
  },

  render() {
    this.$el.fadeOut(500, function () {
      this.$el.html(template(this.templateData()));
      this.$el.fadeIn(500);
    }.bind(this));
  },

  templateData() {
    return {
      sites: this.state.get('teaserSites').toJSON(),
    };
  },

  randomizeTeaser() {
    // Choose a random set of sites to display teaser grades for. If the sum of
    // the site's names is too great, the spans will wrap around within the
    // containing div, which looks weird. This code avoids that problem by
    // re-sampling until a sample that does not trigger the issue is found.
    const maxSiteNamesLength = 50; // Determined empirically
    let teaserSites = null;
    let siteNamesLength = null;
    do {
      teaserSites = new Sites(this.collection.sample(TEASER_SAMPLE_SIZE));
      siteNamesLength = teaserSites.reduce(function(memo, site) {
        return memo + site.get('name').length;
      }, 0);
    } while (siteNamesLength > maxSiteNamesLength);

    this.state.set({
      teaserSites: teaserSites,
    })
  },

  stopRandomizingTeaser() {
    clearInterval(this.timer);
  },

  startRandomizingTeaser() {
    this.timer = setInterval(this.randomizeTeaser.bind(this),
                             TEASER_REFRESH_INTERVAL);
  },

});
