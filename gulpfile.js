var gulp = require('gulp');
var chug = require('gulp-chug');

// copy jquery to static folder
gulp.task('jquery', function () {
    return gulp.src(['node_modules/jquery/dist/**/*'])
        .pipe(gulp.dest('static/jquery/'));
});

// build semantic ui (config: semantic.json)
gulp.task('semantic-ui', function () {
    return gulp.src('semantic/gulpfile.js')
        .pipe(chug({
            tasks: ['build']
        }));
});

// build everything
gulp.task('build', [
    'jquery',
    'semantic-ui'
]);