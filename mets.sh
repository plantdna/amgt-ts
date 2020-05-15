#!/bin/bash
function version()
{
    echo "Version 1.9.0, 2020.05.01"
}

function usage()
{
    echo "Use launch.sh to start as an example, or"
    echo ""
    echo "./mets.sh"
    echo "-h | --help, show this help."
    echo "-s | --script, specify the script folder."
    echo "-e | --environment, specifiy the environment configuration file."
    echo "-m | --method, specify the analysis method, either precise or broad."
    echo "-v | --version, show the current version."
}

while [ "$1" != "" ]; do
    PARAM=`echo $1 | awk -F= '{print $1}'`
    VALUE=`echo $1 | awk -F= '{print $2}'`
    case $PARAM in
        -h | --help)
            usage
            exit
            ;;
        -s | --script)
            SCRIPT_PATH=$VALUE
            ;;
        -e | --environment)
            ENVIRONMENT=$VALUE
            ;;
        -m | --method)
            METHOD=$VALUE
            ;;
        -v | --version)
            version
            exit
            ;;
        *)
            echo "ERROR: unknown parameter \"$PARAM\""
            usage
            exit 1
            ;;
    esac
    shift
done

echo " ===== Script starts running on `date` ====="

## Step1 preparing
. $ENVIRONMENT
mkdir -p $TMP_DIR

## Step2 index the references
$SCRIPT_PATH/subtools/ref_index.sh

## Step3 SSR finding
if [ $METHOD = "precise" ]; then
    sh $SCRIPT_PATH/subtools/match_SSR_precise.sh
elif [ $METHOD = "broad" ]; then
    sh $SCRIPT_PATH/subtools/match_SSR_broad.sh
fi

echo " ===== Script ends running on `date` ====="
