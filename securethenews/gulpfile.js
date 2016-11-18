var gulp = require('gulp');
var gulpUtil = require('gulp-util');
var sourcemaps = require('gulp-sourcemaps');
var source = require('vinyl-source-stream');
var buffer = require('vinyl-buffer');
var browserify = require('browserify');
var watchify = require('watchify');
var babelify = require('babelify');
var sass = require('gulp-sass');
var plumber = require('gulp-plumber');
var autoprefixer = require('gulp-autoprefixer');
var livereload = require('gulp-livereload');
var jadeify = require('jadeify');

const buildDir = './client/build';

gulp.task('js', function() {
  var bundler = browserify('./client/src/javascript/index.js', {
      debug: true
    }).transform(jadeify)
      .transform(babelify);

  bundler = watchify(bundler, {
    poll: true
  });

  var rebundle = function() {
    return bundler.bundle()
      .on('error', function(err) {
        console.error(err);
        this.emit('end');
      })
      .pipe(source('build.js'))
      .pipe(buffer())
      .pipe(sourcemaps.init({ loadMaps: true }))
      .pipe(sourcemaps.write('./'))
      .pipe(gulp.dest(buildDir))
      .pipe(livereload())
      .on('end', function() {
        gulpUtil.log('build.js rebuilt');
      });
  }

  bundler.on('update', rebundle);
  return rebundle();
});

gulp.task('js:production', function() {
  return browserify('./client/src/javascript/index.js', {
    debug: false
  }).transform(jadeify)
    .transform('babelify', {presets: ["es2015"]})
    .bundle()
    .pipe(source('build.js'))
    .pipe(gulp.dest(buildDir))
    .on('error', function() {
      gulpUtil.log('JS error: <%= error.message %>')
    })
    .on('end', function() {
      gulpUtil.log('production js built');
    })
});

gulp.task('styles', function() {
  return gulp.src('client/src/styles/main.scss')
    .pipe(plumber())
    .pipe(sass({
      includePaths: ['node_modules/']
    }).on('error', sass.logError))
    .pipe(autoprefixer())
    .pipe(gulp.dest(buildDir))
    .pipe(livereload())
    .on('error', gulpUtil.log);
});

gulp.task('build:production', ['styles', 'js:production']);

gulp.task('watch', ['styles', 'js'], function() {
  livereload.listen();
  gulp.watch('./client/src/**/*.scss', ['styles']);
});

gulp.task('default', ['watch']);
