import io
import zipfile
import plotly

def export_plots(data, export_format):
    plots_dict = data.getPlots()
    plots_to_zip = {}
    for name_plots in plots_dict:
        exported_plot = plotly.io.from_json(plots_dict[name_plots])
        if export_format in ["png", "jpeg", "svg", "pdf"]:
            buffer_img = io.BytesIO()
            fig_in_byte = exported_plot.to_image(format=export_format)
            # fig_in_byte.save(buffer_img, export_format)
            buffer_img.write(fig_in_byte)
            buffer_img.seek(0)

            plot_file = name_plots + "." + export_format
            plots_to_zip[plot_file] = buffer_img

    return plots_to_zip


def get_zip_buffer(data, export_format):
    zip_buffer = io.BytesIO()

    plots_to_zip = export_plots(data, export_format)

    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for file_name, data in plots_to_zip.items():
            zip_file.writestr(file_name, data.read())

    zip_buffer.seek(0)
    return zip_buffer

