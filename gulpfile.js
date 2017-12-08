var gulp = require('gulp');
var chug = require('gulp-chug');

gulp.task('jquery', function () {
    return gulp.src(['node_modules/jquery/dist/**/*'])
        .pipe(gulp.dest('static/jquery/'));
});

gulp.task('semantic-ui', function () {
    return gulp.src('semantic/gulpfile.js')
        .pipe(chug({
            tasks: ['build']
        }));
});

gulp.task('build', [
    'jquery',
    'semantic-ui'
]);