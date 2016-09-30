const Backbone = require('backbone');
const _ = require('underscore');
const $ = require('jquery');
const Sites = require('./sites.js');
const template = require('./leaderboardtemplate.jade');

module.exports = Backbone.View.extend({
  initialize() {
    // Instantiate collection using data injected into the template server-side
    this.collection = new Sites(window.STNsiteData);

    // Model to hold the current state of the leaderboard controls
    this.state = new Backbone.Model({
      searchString: '',
      orderBy: 'score',
      order: 'desc'
    });

    // Re-render the view whenever anything changes
    this.listenTo(this.state, 'change', this.render);

    // Update the sort when the headings are clicked
    this.$el.on( 'click', '.sort-control', _.bind(this.updateSort, this));

    // Update the search string whenever text is entered
    $('[name=search]').on('input', (event) => {
        this.state.set('searchString', event.target.value.toLowerCase());
    });
  },

  render() {
    this.$el.html(template(this.templateData()));
  },

  templateData() {
    let models = this.collection.toJSON();
    models = _.filter(models, (site) => {
      return site.name.toLowerCase().indexOf(this.state.get('searchString')) !== -1
        || site.url.toLowerCase().indexOf(this.state.get('searchString')) !== -1;
    });

    // This will sort false first, and lowest number first
    models = _.sortBy(models, this.state.get('orderBy'))

    if (this.state.get('order') == 'asc') {
      models = models.reverse();
    }

    return {
      items: models,
      state: this.state.toJSON(),
    };
  },

  updateSort(event) {
    const sortKey = $(event.currentTarget).data('sort-key');
    if (this.state.get('orderBy') == sortKey) {
      this.state.set('order', this.state.get('order') == 'desc' ? 'asc' : 'desc');
    } else {
      this.state.set({
        orderBy: sortKey,
        order: 'desc',
      });
    }
  },

  // Map true/false/null values to 1/-1/0 to allow for easy sorting
  transformData(rawData) {
    return _.map(rawData, (d) => {
      return _.extend({}, d, {
        downgrades_https: mapValue(d.downgrades_https),
        valid_https: mapValue(d.valid_https),
        default_https: mapValue(d.default_https),
        enforces_https: mapValue(d.enforces_https),
      });
    });
  }

});


const mapValue = function(value) {
  if (value === true) {
    return 1;
  } else if (value === false) {
      return -1;
  } else {
    return 0;
  }
};
