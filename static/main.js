(function (document) {
    var papers = document.getElementsByClassName('paper');

    for (var i = 0; i < papers.length; i++) {
        var link = papers[i].getElementsByClassName('summary-toggle')[0];
        var summaryShort = papers[i].getElementsByClassName('summary-short')[0];
        var fullLink = papers[i].getElementsByClassName('summary-more')[0];
        var summaryText = papers[i].getElementsByClassName('summary-text')[0];
        var summaryFull = papers[i].getElementsByClassName('summary-full')[0];
        var summaryMore = papers[i].getElementsByClassName('summary-more')[0];

        var addSummaryEvent = function (link, fullLink, summary, summaryText, summaryFull, summaryMore) {
            /* link.addEventListener('click', function () {
                if (summary.style.display === 'none') {
                    summary.style.display = 'block';
                } else {
                    summary.style.display = 'none';
                }
            });*/

            fullLink.addEventListener('click', function () {
                if (summaryFull.style.display == 'none') {
                    summaryMore.innerHTML = '&laquo; Less'
                    summaryFull.style.display = 'inline';
                    summaryText.style.display = 'none';
                } else {
                    summaryMore.innerHTML = 'More &raquo;'
                    summaryFull.style.display = 'none';
                    summaryText.style.display = 'inline';
                }
            });
        };
        // summaryShort.style.display = 'none';
        summaryFull.style.display = 'none';

        addSummaryEvent(link, fullLink, summaryShort, summaryText, summaryFull, summaryMore);

        var id = papers[i].dataset.id;
        var markRead = papers[i].getElementsByClassName('mark-read')[0];
        var markLater = papers[i].getElementsByClassName('mark-later')[0];
        var markNone = papers[i].getElementsByClassName('mark-none')[0];
        var radioRead = papers[i].getElementsByClassName('radio-read')[0];
        var radioLater = papers[i].getElementsByClassName('radio-later')[0];
        var radioNone = papers[i].getElementsByClassName('radio-none')[0];

        var addMarkEvent = function (id, read, later, none) {
            var request;

            var addEvent = function (element, className, id, mark) {
                var radio = element.getElementsByClassName(className);

                if (radio.length > 0) {
                    radio = radio[0];

                    radio.addEventListener('click', function () { updateMark(id, mark); });
                }
            }

            var updateRadio = function (mark) {
                if (mark == 'read') {
                    read.innerHTML = 'Read';
                    later.innerHTML = '<a class="mark-later">Read Later</a>';
                    none.innerHTML = '<a class="mark-none">None</a>';
                } else if (mark == 'later') {
                    read.innerHTML = '<a class="mark-read">Read</a>';
                    later.innerHTML = 'Read Later';
                    none.innerHTML = '<a class="mark-none">None</a>';
                } else if (mark == 'none') {
                    read.innerHTML = '<a class="mark-read">Read</a>';
                    later.innerHTML = '<a class="mark-later">Read Later</a>';
                    none.innerText = 'None';
                }

                addEvent(read, 'mark-read', id, 'read');
                addEvent(later, 'mark-later', id, 'later');
                addEvent(none, 'mark-none', id, 'none');
            }

            var getResponse = function () {
                if (request.readyState === XMLHttpRequest.DONE) {
                    if (request.status === 200) {
                        updateRadio(request.responseText);
                    }
                }
            }

            var updateMark = function (id, mark) {
                request = new XMLHttpRequest();

                if (!request) {
                    return false;
                }

                request.onreadystatechange = getResponse;
                request.open('GET', window.location.origin + '/mark/' + id + '/' + mark);
                request.send();
            };

            addEvent(read, 'mark-read', id, 'read');
            addEvent(later, 'mark-later', id, 'later');
            addEvent(none, 'mark-none', id, 'none');
        };

        addMarkEvent(id, radioRead, radioLater, radioNone);
    }
})(document);