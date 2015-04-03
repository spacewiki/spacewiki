var gulp = require('gulp');
var sass = require('gulp-sass');

var paths = {
  scripts: [
    'bower_components/modernizr/modernizr.js',
    'bower_components/jquery/dist/jquery.js',
    'bower_components/foundation/js/foundation.js',
    'bower_components/jquery.stellar/jquery.stellar.js',
    'node_modules/css-polyfills/dist/css-polyfills.js',
    'theme/js/*.js'
  ],
  scss: ['theme/app.scss'],
  images: ['theme/img/**/*'],
  content_img: ['content/pictures/**/*']
};

gulp.task('scss', function() {
  return gulp.src(paths.scss)
    .pipe(sass({
      includePaths: ['node_modules/foundation/scss/']
    }))
    .pipe(gulp.dest('static/lib/'));
});

gulp.task('default', ['scss']);
