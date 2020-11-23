import Backbone from 'backbone'
import _ from 'underscore'
import $ from 'jquery'
import Sites from './sites'
import template from './leaderboardtemplate.jade'

export default Backbone.View.extend({
  initialize(options) {
    const optionsDefaults = {
      // Display this many results; if null, show all
      limit: null,
      // Enable interactive features; on by default
      interactive: true,
    };
    this.options = _.defaults(options, optionsDefaults);

    // Instantiate collection using data injected into the template server-side
    this.collection = new Sites(window.STNsiteData);

    // Model to hold the current state of the leaderboard controls
    this.state = new Backbone.Model({
      searchString: '',
      orderBy: 'score',
      order: 'desc',
    });

    // Re-render the view whenever anything changes
    this.listenTo(this.state, 'change', this.render);

    // Register event handlers for interactive functionality, if enabled
    if (this.options.interactive) {
      // Update the sort when the headings are clicked
      this.$el.on('click', '.sort-control', this.updateSort.bind(this));

      // Update the search string whenever text is entered
      $('[name=search]').on('input', this.updateSearch.bind(this));

      // Bind scroll listener to float leaderboard table header when we're
      // scrolled past it
      $(window).bind('scroll', this.floatThead.bind(this));
    }
  },

  render() {
    this.$el.html(template(this.templateData()));
    if (this.options.interactive === true) {
      // When the template is re-rendered, the old DOM nodes are lost. Reset!
      this.resetHeader();
    }
  },

  templateData() {
    let models = this.collection.toJSON();
    models = _.filter(models, (site) => {
      return site.name.toLowerCase().indexOf(this.state.get('searchString')) !== -1
        || site.domain.toLowerCase().indexOf(this.state.get('searchString')) !== -1;
    });

    models = _.sortBy(models, this.state.get('orderBy'))

    if (this.state.get('orderBy') == 'https_available') {
      models = _.sortBy(models, function(item) {
        return item.valid_https && !item.downgrades_https
      })
    }

    if (this.state.get('order') == 'desc') {
      models = models.reverse();
    }

    if (this.options.limit !== null) {
      models = models.slice(0, this.options.limit);
    }

    return {
      items: models,
      state: this.state.toJSON(),
    };
  },

  updateSort(event) {
    const sortKey = $(event.currentTarget).data('sort-key');
    if (this.state.get('orderBy') == sortKey) {
      this.state.set({
        order: this.state.get('order') == 'desc' ? 'asc' : 'desc',
      });
    } else {
      this.state.set({
        orderBy: sortKey,
        order: 'desc',
      });
    }
  },

  updateSearch(event) {
    this.state.set({
      searchString: event.target.value.toLowerCase(),
    });
  },

  floatThead(event) {
    let $header = $('#header-normal > thead');

    // Scroll listener may fire before the template has been rendered - return
    // without doing anything (nothing to do).
    if ($header.length === 0) {
      return;
    }

    if (!this.$fixedHeader) {
      this.$fixedHeader = $('#header-fixed').append($header.clone());
    }

    let tableOffset = $header.offset().top;
    let offset = $(window).scrollTop();
    let $fixedHeader = this.$fixedHeader;

    if (offset >= tableOffset && $fixedHeader.is(":hidden")) {
      $fixedHeader.show();
      // Update the fixed header with th widths from the normal header. In the
      // normal header, the widths are computed based on the table contents, but
      // the #fixed-header table only has the header, so we need to explicitly
      // copy the correct widths.
      $.each($header.find('tr > th'), function(i, el) {
        let originalWidth = $(el).width();
        $($fixedHeader.find('tr > th')[i]).width(originalWidth);
      });
    } else if (offset < tableOffset && $fixedHeader.is(":visible")) {
      $fixedHeader.hide();
    }
  },

  resetHeader() {
    this.$fixedHeader = null;
    this.floatThead();
  },

});
