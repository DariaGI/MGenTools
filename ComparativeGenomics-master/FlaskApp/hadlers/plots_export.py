import plotly

def export_plots(data, export_format):
    plots_dict = data.getPlots()
    for name_plots in plots_dict:
        exported_plot = plotly.io.read_json(plots_dict[name_plots])
        if export_format in ["png", "jpeg", "svg", "pdf"]:
            exported_plot.write_image(name_plots + "." + export_format)

