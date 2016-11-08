const Backbone = require('backbone');
const _ = require('underscore');
const $ = require('jquery');
const Sites = require('./sites.js');
const template = require('./teasertemplate.jade');

const teaserRefreshInterval = 5000;

module.exports = Backbone.View.extend({

  initialize() {
    // Instantiate collection using data injected into the template server-side
    this.collection = new Sites(window.STNsiteData);

    // Subset of sites from the collection to display
    this.sites = new Sites();

    // Timer to periodically refresh the set of random sites in the teaser
    this.timer = null;

    // Initial set of random sites
    this.randomizeTeaser();

    // Re-render the view whenever anything changes
    this.listenTo(this.sites, 'reset', this.rotateTeaser);

    // Start periodically refreshing the set of random sites in the teaser
    this.startRandomizingTeaser();

    // Pause the periodic refresh when the user hovers over the teaser, and
    // resume when they move the cursor away.
    this.$el.hover(this.stopRandomizingTeaser.bind(this),
                   this.startRandomizingTeaser.bind(this));
  },

  render() {
    this.$el.html(template(this.templateData()));
  },

  templateData() {
    return {
      sites: this.sites.toJSON(),
    };
  },

  rotateTeaser() {
    const fadeDuration = 500;
    this.$el.fadeOut(fadeDuration, () => {
      this.render();
      this.$el.fadeIn(fadeDuration);
    })
  },

  randomizeTeaser() {
    const teaserSampleSize = 3;
    const teaserSites = new Sites();

    // Choose a random set of sites to display teaser grades for. If the sum of
    // the site's names is too great, the spans will wrap around within the
    // containing div, which looks weird. This code avoids that problem by
    // re-sampling until a sample that does not trigger the issue is found.
    const maxSiteNamesLength = 50; // Determined empirically
    let siteNamesLength = null;
    do {
      teaserSites.reset(this.collection.sample(teaserSampleSize));
      siteNamesLength = teaserSites.reduce(function(memo, site) {
        return memo + site.get('name').length;
      }, 0);
    } while (siteNamesLength > maxSiteNamesLength);

    this.sites.reset(teaserSites.models);
  },

  stopRandomizingTeaser() {
    clearInterval(this.timer);
  },

  startRandomizingTeaser() {
    this.timer = setInterval(this.randomizeTeaser.bind(this),
                             teaserRefreshInterval);
  },

});
