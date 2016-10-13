var gulp = require('gulp');
var gulpUtil = require('gulp-util');
var sourcemaps = require('gulp-sourcemaps');
var source = require('vinyl-source-stream');
var buffer = require('vinyl-buffer');
var browserify = require('browserify');
var watchify = require('watchify');
var babel = require('babelify');
var sass = require('gulp-sass');
var plumber = require('gulp-plumber');
var autoprefixer = require('gulp-autoprefixer');
var livereload = require('gulp-livereload');
var jadeify = require('jadeify');


function compile(watch) {
  var bundler = watchify(browserify('./client/src/javascript/index.js', { debug: true })
    .transform(jadeify)
    .transform(babel),
    { poll: true });

  function rebundle() {
    bundler.bundle()
      .on('error', function(err) { console.error(err); this.emit('end'); })
      .pipe(source('build.js'))
      .pipe(buffer())
      .pipe(sourcemaps.init({ loadMaps: true }))
      .pipe(sourcemaps.write('./'))
      .pipe(gulp.dest('./client/build'))
      .pipe(livereload())
      .on('end', function() {
        gulpUtil.log('build.js rebuilt');
      });
  }

  if (watch) {
    bundler.on('update', rebundle);
  }

  rebundle();
}

// Compile Sass to css
gulp.task('styles', function() {
  gulp.src('client/src/styles/main.scss')
    .pipe(plumber())
    .pipe(sass({
      includePaths: ['node_modules/']
    }).on('error', sass.logError))
    .pipe(autoprefixer())
    .pipe(gulp.dest('./client/build'))
    .pipe(livereload())
    .on('error', gulpUtil.log);
});

// TODO: Lint all the javascript task

function watch() {
  livereload.listen();
  gulp.watch('client/src/**/*.scss', ['styles']);
  return compile(true);
};

gulp.task('build', function() { return compile(); });
gulp.task('watch', function() { return watch(); });

gulp.task('default', ['watch', 'styles']);;
