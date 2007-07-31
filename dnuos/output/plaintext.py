"""Plain-text renderer"""

import time

from dnuos.output.abstract_renderer import AbstractRenderer

class Renderer(AbstractRenderer):

    def render(self, dir_pairs, options, data):

        """Render directories to a sequence of strings."""
        output = [
            (lambda: options.disp_date,
             self.render_date()),
            (lambda: True,
             self.render_directories(dir_pairs, not options.stripped)),
            (lambda: data.bad_files,
             self.render_bad_files(data.bad_files)),
            (lambda: options.disp_time,
             self.render_generation_time(data.times)),
            (lambda: options.disp_result,
             self.render_sizes(data.size, data.times)),
            (lambda: options.disp_version,
             render_version(data.version)),
        ]
        first = True
        for pred, renderer in output:
            if pred():
                if not first:
                    yield ''
                for chunk in renderer:
                    yield chunk
                first = False

    def render_date(self):

        yield time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())

    def render_directories(self, dir_pairs, show_headers=True):

        if show_headers:
            fields = [c.header() for c in self.columns]
            line = self.format_string % tuple(fields)
            yield line
            yield "=" * len(line)

        for adir, root in dir_pairs:
            fields = [ c.get_formatted(adir, root) for c in self.columns ]
            yield self.format_string % tuple(fields)

    def render_bad_files(self, bad_files):

        yield "Audiotype failed on the following files:"
        yield "\n".join(bad_files)

    def render_generation_time(self, times):

        yield "Generation time:     %8.2f s" % times['elapsed_time']

    def render_sizes(self, sizes, times):

        line = "+-----------------------+-----------+"

        yield line
        yield "| Format    Amount (Mb) | Ratio (%) |"
        yield line
        for mediatype in ["Ogg", "MP3", "MPC", "AAC", "FLAC"]:
            if sizes[mediatype]:
                yield "| %-8s %12.2f | %9.2f |" % (
                    mediatype,
                    sizes[mediatype] / (1024 * 1024),
                    sizes[mediatype] * 100 / sizes["Total"])
        yield line
        total_megs = sizes["Total"] / (1024 * 1024)
        yield "| Total %10.2f Mb   |" % total_megs
        yield "| Speed %10.2f Mb/s |" % (total_megs / times['elapsed_time'])
        yield line[:25]


def render_version(version):

    yield "dnuos " + version
