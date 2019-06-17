###############################################################################
# Version 1.0.0. Written by Rhys Rawlings.                                    #
###############################################################################
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def main():
    """
    TITLE
    ---------------------------------------------------------------------------
    main
    ---------------------------------------------------------------------------

    DESCRIPTION
    ---------------------------------------------------------------------------
    This function is the starting point for the program and will run all other
    functions
    ---------------------------------------------------------------------------

    FUNCTIONS USED
    ---------------------------------------------------------------------------
    import_clean_process
    plot_data_matplotlib
    ---------------------------------------------------------------------------

    ARGUMENTS
    ---------------------------------------------------------------------------
    None
    ---------------------------------------------------------------------------

    GLOBAL VARIABLES (variables used that are defined outside of this function)
    ---------------------------------------------------------------------------
    None
    ---------------------------------------------------------------------------

    OUTPUT
    ---------------------------------------------------------------------------
    None
    ---------------------------------------------------------------------------
    """
    df_data = import_clean_process()
    plot_data_matplotlib(df_data)
    return


def import_clean_process():
    """
    TITLE
    ---------------------------------------------------------------------------
    import_clean_process
    ---------------------------------------------------------------------------

    DESCRIPTION
    ---------------------------------------------------------------------------
    This function imports, cleans and prepares the data for visualisation and
    analysis
    ---------------------------------------------------------------------------

    FUNCTIONS USED
    ---------------------------------------------------------------------------
    None
    ---------------------------------------------------------------------------

    ARGUMENTS
    ---------------------------------------------------------------------------
    None
    ---------------------------------------------------------------------------

    GLOBAL VARIABLES (variables used that are defined outside of this function)
    ---------------------------------------------------------------------------
    None
    ---------------------------------------------------------------------------

    OUTPUT
    ---------------------------------------------------------------------------
    RETURNS
    df_data: pandas dataframe
        this is a dataframe which contains the data 
    ---------------------------------------------------------------------------
    """
    # loading the co2 emissions data for the Earth, I'm only interested in the
    # total emissions and the year
    global_co2 = pd.read_csv(
        "datasets/Global CO2 Emissions.csv",
        usecols=[
            "Year",
            "Total"
        ],
        parse_dates=["Year"],
        index_col="Year"
    )
    # creating the global temperature dataframe
    global_temp_data = open(
        "datasets/CRUTEM.4.6.0.0.global_n+s",
        "r"
    )
    global_temp = pd.DataFrame(
        {
            "global_temp": [],
        }
    )
    for line in global_temp_data:
        # each line in the file is an observation for the year, the first
        # column being the year, the second being the temperature measurement
        data = line.split()
        global_temp.at[pd.to_datetime(data[0]), "global_temp"] = float(data[1])
    global_temp_data.close()
    # loading the co2 emissions data for the UK
    uk_co2 = pd.read_csv(
        "datasets/UK carbon dioxide emissions between 1858 to 2017 .csv",
        parse_dates=["Date"],
        index_col="Date"
    )
    # creating the dataframe for the UK temperature data
    uk_temp = pd.DataFrame(
        {
            "uk_temp": [],
        }
    )
    # this file consists of monthly and seasonal averages for the UK surface
    # temperature
    uk_tmean = open(
        "datasets/UK Mean Temperature (Degrees C)",
        "r"
    )
    for index, line in enumerate(uk_tmean):
        # the data begins on the eigth line in the file
        if index > 7:
            data = line.split()
            # the monthly temperatures are from the 2nd and 13th columns
            month_temps = np.array(data[1:13]).astype(float)
            # the first reading is the year, I've taken the average of all the
            # months to get an annual average
            uk_temp.at[pd.to_datetime(data[0]), "uk_temp"] = month_temps.mean()
    uk_tmean.close()
    # removing the temperature reading for 2019 as it isn't averaged over the
    # whole year (this program was written in 06/2019)
    uk_temp = uk_temp[:-1]
    # merging the temperature and co2 emissions dataframes for the Earth
    global_data = pd.merge(
        global_temp,
        global_co2,
        left_index=True,
        right_index=True,
        how="outer"
    )
    # merging the temperature and co2 emissions dataframes for the UK
    uk_data = pd.merge(
        uk_temp,
        uk_co2,
        left_index=True,
        right_index=True,
        how="outer"
    )
    # merging the global and UK dataframes
    df_data = pd.merge(
        global_data,
        uk_data,
        left_index=True,
        right_index=True,
        how="outer"
    )
    # rename some of the columns to make them more clear
    df_data = df_data.rename(
        columns={
            "Total": "global_co2",
            "CO2 Emissions": "uk_co2"
        }
    )
    return df_data


def plot_data_matplotlib(df_data):
    """
    TITLE
    ---------------------------------------------------------------------------
    plot_data_matplotlib
    ---------------------------------------------------------------------------

    DESCRIPTION
    ---------------------------------------------------------------------------
    This function plots the data taken as an argument using the matplotlib
    library
    ---------------------------------------------------------------------------

    FUNCTIONS USED
    ---------------------------------------------------------------------------
    None
    ---------------------------------------------------------------------------

    ARGUMENTS
    ---------------------------------------------------------------------------
    df_data: pandas dataframe
        this is a dataframe that contains the data
    ---------------------------------------------------------------------------

    GLOBAL VARIABLES (variables used that are defined outside of this function)
    ---------------------------------------------------------------------------
    None
    ---------------------------------------------------------------------------

    OUTPUT
    ---------------------------------------------------------------------------
    A figure that plots the data in df_data as two subplots with shared x axes
    ---------------------------------------------------------------------------
    """
    # creating the figure and subplots as two rows and one column
    fig, ax = plt.subplots(2, 1)
    # defining the colours used for the plots and y axes
    red = "#DA2525"
    blue = "#003A78"
    # setting up the subplots to share the x axis
    # ax02 is the second y axis of the first subplot
    ax02 = ax[0].twinx()
    # ax12 is the second y axis of the second subplot
    ax12 = ax[1].twinx()
    # the global co2 line plot
    line1 = ax[0].plot(
        df_data.index,
        df_data["global_co2"],
        label="Global $CO_2$ Emissions",
        color=blue
    )
    # the global temperature line plot
    line2 = ax02.plot(
        df_data.index,
        df_data["global_temp"],
        label="Global Temperature Anomaly",
        color=red
    )
    # the uk co2 line plot
    line3 = ax[1].plot(
        df_data.index,
        df_data["uk_co2"],
        label="UK $CO_2$ Emissions",
        color=blue
    )
    # the uk temperature line plot
    line4 = ax12.plot(
        df_data.index,
        df_data["uk_temp"],
        label="UK Surface Temperature",
        color=red
    )
    # the next three dataframes are used to indicate where there are gaps in
    # the data, which I will use to produce a shaded region to highlight this
    # fact
    # for the global temperature data
    global_temp_nan = df_data[pd.isna(df_data["global_temp"])]
    # for the UK temperature data
    uk_temp_nan = df_data[pd.isna(df_data["uk_temp"])][:-1]
    # for the UK co2 emissions data
    uk_co2_nan = df_data[pd.isna(df_data["uk_co2"])][:-2]
    # creating a shaded region to show the missing global temperature data
    ax[0].axvspan(
        global_temp_nan.index[0],
        global_temp_nan.index[-1],
        alpha=0.1,
        color="black"
    )
    # creating a shaded region to show the missing UK co2 data
    ax[1].axvspan(
        uk_temp_nan.index[0],
        uk_co2_nan.index[-1],
        alpha=0.1,
        color="black"
    )
    # creating a shaded region to show the missing UK temperature data
    ax[1].axvspan(
        uk_co2_nan.index[-1],
        uk_temp_nan.index[-1],
        alpha=0.05,
        color="black"
    )
    # setting titles for the figure and subplots
    ax[0].set_title("{}{}{}".format(
        "Global and UK ",
        "$CO_2$ Emissions and Surface Temperature over Time",
        "\n\nGlobal"))
    ax[1].set_title("UK")
    # setting axes labels
    ax[1].set_xlabel("Time (years)")
    ax[0].set_ylabel("$CO_2$ Emissions (Tg)", color=blue)
    ax02.set_ylabel("Temperature Anomaly (°C)", color=red)
    ax[1].set_ylabel("$CO_2$ Emissions (Tg)", color=blue)
    ax12.set_ylabel("Temperature (°C)", color=red)
    # setting x axes limits so both subplots are over the same range
    ax[0].set_xlim((df_data.index[0], df_data.index[-1]))
    ax[1].set_xlim((df_data.index[0], df_data.index[-1]))
    # setting the x axes tick values
    ax[0].set_xticks([d for d in df_data.index if d.year % 20 == 0])
    ax[1].set_xticks([d for d in df_data.index if d.year % 20 == 0])
    # setting y axes colours to match the line plots
    ax[0].tick_params("y", colors=blue)
    ax02.tick_params("y", colors=red)
    ax[1].tick_params("y", colors=blue)
    ax12.tick_params("y", colors=red)
    # annotating the shaded regions
    ax[0].annotate(
        "No temperature data available",
        ("1760-01-01", 4000)
    )
    ax[1].annotate(
        "No data available",
        ("1760-01-01", 300)
    )
    ax[1].annotate(
        "No temperature data available",
        ("1850-01-01", 500)
    )
    # setting the legends    
    ax[0].legend(
        line1 + line2,
        [
            line1[0].get_label(),
            line2[0].get_label(),
        ],
        loc=2
    )
    ax[1].legend(
        line3 + line4,
        [
            line3[0].get_label(),
            line4[0].get_label()
        ],
        loc=2
    )
    plt.show()
    return


main()
