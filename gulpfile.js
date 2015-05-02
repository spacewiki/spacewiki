var gulp = require('gulp');
var sass = require('gulp-sass');
var uglify = require('gulp-uglify');
var concat = require('gulp-concat');
var copy = require('gulp-copy');

var paths = {
  scripts: [
    'node_modules/jquery/dist/jquery.js',
    'node_modules/jquery.cookie/jquery.cookie.js',
    'theme/js/lib/**/*.js',
    'theme/js/*.js'
  ],
  scss: ['theme/app.scss'],
  images: ['theme/img/**/*'],
  content_img: ['content/pictures/**/*']
};

gulp.task('images', function() {
  return gulp.src(paths.images)
    .pipe(copy('static/img/', {prefix: 2}));
});

gulp.task('scripts', function() {
  return gulp.src(paths.scripts)
    .pipe(uglify())
    .pipe(concat('app.min.js'))
    .pipe(gulp.dest('static/lib/'));
});

gulp.task('scss', function() {
  return gulp.src(paths.scss)
    .pipe(sass({
      includePaths: ['node_modules/foundation/scss/']
    }))
    .pipe(gulp.dest('static/lib/'));
});

gulp.task('default', ['scss', 'scripts', 'images']);
