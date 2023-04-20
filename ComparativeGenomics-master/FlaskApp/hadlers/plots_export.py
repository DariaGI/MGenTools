import plotly
import zipfile
# import io
#
# def export_plots(data, export_format):
#     plots_dict = data.getPlots()
#     plots_to_zip = []
#     for name_plots in plots_dict:
#         exported_plot = plotly.io.from_json(plots_dict[name_plots])
#         if export_format in ["png", "jpeg", "svg", "pdf"]:
#             plot_file = name_plots + "." + export_format
#             exported_plot.write_image(plot_file)
#             plots_to_zip.append(plot_file)
#
#     zip_buffer = io.BytesIO()
#     with zipfile.ZipFile(zip_buffer, "w") as zf:
#         for files in plots_to_zip:
#             zf.write(files)
#
#     return zf

#Отправка архива обычного


def export_plots(data, export_format):
    plots_dict = data.getPlots()
    plots_to_zip = []
    for name_plots in plots_dict:
        exported_plot = plotly.io.read_json(plots_dict[name_plots])
        if export_format in ["png", "jpeg", "svg", "pdf"]:
            plot_file = name_plots + "." + export_format
            exported_plot.write_image(plot_file)
            plots_to_zip.append(plot_file)
    zf = zipfile.ZipFile("all_plots.zip", "w")
    for files in plots_to_zip:
        zf.write(files)
    zf.close()
    return "all_plots.zip"






