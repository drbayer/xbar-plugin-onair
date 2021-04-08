#!/bin/sh

# Metadata allows your plugin to show up in the app, and website.
#
#  <xbar.title>Zoom On-Air</xbar.title>
#  <xbar.version>v0.1</xbar.version>
#  <xbar.author>David Bayer</xbar.author>
#  <xbar.author.github>drbayer</xbar.author.github>
#  <xbar.desc>Changes color of Magic Hue smart bulbs to indicate when you're in a Zoom meeting.</xbar.desc>
#  <xbar.image>http://www.hosted-somewhere/pluginimage</xbar.image>
#  <xbar.dependencies>python3,virtualenv</xbar.dependencies>
#  <xbar.abouturl>http://url-to-about.com/</xbar.abouturl>
# 
#  <xbar.var>string(ONAIR_LIGHTS="first"): Addresses of lights to control. Defaults to first bulb found on network.</xbar.var>
#  <xbar.var>boolean(ONAIR_OFFAIR_LIGHTON=false): Should the light be turned on when not in a meeting?</xbar.var>
#  <xbar.var>string(ONAIR_ONAIR_COLOR="ff0000"): Hex code for bulb color when on-air. Defaults to red.</xbar.var>
#  <xbar.var>number(ONAIR_ONAIR_BRIGHTNESS=255): Brightness level when on-air. Range is 0-255.</xbar.var>
#  <xbar.var>string(ONAIR_OFFAIR_COLOR="00ff00"): Hex code for bulb color when off-air. Defaults to green.</xbar.var>
#  <xbar.var>number(ONAIR_OFFAIR_BRIGHTNESS=255): Brightness level when off-air. Range is 0-255.</xbar.var>
#
# Use Magic Hue smart light bulbs to indicate when you are in a Zoom meeting.
#
# xbar-onair.py built from original work by Tim Toll.
# xbar-onair.15s.sh borrowed from Paul (infothrill) https://github.com/infothrill/bitbar-plugin-pingdom/blob/master/bitbar-pingdom.60s.sh
#

SELF_PATH=$(cd -P -- "$(dirname -- "$0")" && pwd -P) && SELF_PATH=$SELF_PATH/$(basename -- "$0")
# resolve symlinks
while [ -h "$SELF_PATH" ]; do
    # 1) cd to directory of the symlink
    # 2) cd to the directory of where the symlink points
    # 3) get the pwd
    # 4) append the basename
    DIR=$(dirname -- "$SELF_PATH")
    SYM=$(readlink "$SELF_PATH")
    SELF_PATH=$(cd "$DIR" && cd "$(dirname -- "$SYM")" && pwd)/$(basename -- "$SYM")
done

PROGNAME="$(basename "$SELF_PATH")"

error_exit()
{
	echo "${PROGNAME}: ${1:-"Unknown Error"}" 1>&2
	exit 1
}

PLUGIN_DIR="$(dirname "${SELF_PATH}")/xbar-onair"
cd "${PLUGIN_DIR}" || error_exit "cd ${PLUGIN_DIR}"

if ! test -d env; then
    # standard macOS does not ship 'virtualenv', so let's add /usr/local/bin to the PATH:
    export PATH=/usr/local/bin:$PATH
    virtualenv env
    # shellcheck disable=SC1091
    . env/bin/activate
    pip3 install magichue
fi
# shellcheck disable=SC1091
. env/bin/activate
export LANG="${LANG:-en_US.UTF-8}"  # needed when printing utf-8 chars
exec ./xbar-onair.py
