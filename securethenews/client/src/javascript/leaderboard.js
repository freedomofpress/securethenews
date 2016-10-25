const Backbone = require('backbone');
const _ = require('underscore');
const $ = require('jquery');
const Sites = require('./sites.js');
const template = require('./leaderboardtemplate.jade');

const PAGE_SIZE = 10;

module.exports = Backbone.View.extend({
  initialize() {
    // Instantiate collection using data injected into the template server-side
    this.collection = new Sites(window.STNsiteData);

    // Model to hold the current state of the leaderboard controls
    this.state = new Backbone.Model({
      searchString: '',
      orderBy: 'score',
      order: 'desc',
      page: 0,
    });

    // Re-render the view whenever anything changes
    this.listenTo(this.state, 'change', this.render);

    // Update the sort when the headings are clicked
    this.$el.on('click', '.sort-control', this.updateSort.bind(this));

    // Hook up pagination
    this.$el.on('click', '.pagination .next', this.updatePage.bind(this, 1));
    this.$el.on('click', '.pagination .previous', this.updatePage.bind(this, -1));

    // Update the search string whenever text is entered
    $('[name=search]').on('input', this.updateSearch.bind(this));
  },

  render() {
    this.$el.html(template(this.templateData()));
  },

  templateData() {
    let models = this.collection.toJSON();
    models = _.filter(models, (site) => {
      return site.name.toLowerCase().indexOf(this.state.get('searchString')) !== -1
        || site.domain.toLowerCase().indexOf(this.state.get('searchString')) !== -1;
    });

    // This will sort false first, and lowest number first
    models = _.sortBy(models, this.state.get('orderBy'))

    if (this.state.get('order') == 'asc') {
      models = models.reverse();
    }

    const hasNextPage = models.length > (PAGE_SIZE * (this.state.get('page') + 1));
    const hasPages = models.length > PAGE_SIZE;

    // +1 because pages are 0-indexed, but should be displayed 1-indexed because
    // that is more familiar to non-programmers.
    const pageNumber = this.state.get('page') + 1;
    const totalPages = Math.floor(models.length / PAGE_SIZE) + 1;

    models = models.slice(
      this.state.get('page') * PAGE_SIZE,
      (this.state.get('page') + 1) * PAGE_SIZE);

    return {
      items: models,
      hasNextPage,
      hasPages,
      pageNumber,
      state: this.state.toJSON(),
      totalPages,
    };
  },

  updateSort(event) {
    const sortKey = $(event.currentTarget).data('sort-key');
    if (this.state.get('orderBy') == sortKey) {
      this.state.set({
        order: this.state.get('order') == 'desc' ? 'asc' : 'desc',
        page: 0
      });
    } else {
      this.state.set({
        orderBy: sortKey,
        order: 'desc',
        page: 0,
      });
    }
  },

  updateSearch(event) {
    this.state.set({
      searchString: event.target.value.toLowerCase(),
      page: 0
    });
  },

  updatePage(val) {
    const maxPage = Math.floor(this.collection.length / PAGE_SIZE);
    const newPage = Math.min(maxPage, Math.max(0, this.state.get('page') + val));
    this.state.set({
      page: newPage
    });
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
